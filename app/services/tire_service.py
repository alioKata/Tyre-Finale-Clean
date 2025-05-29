# app/services/tire_service.py

import os
import uuid
import json
import numpy as np
import cv2
import tensorflow as tf
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tire import TireRecord
from typing import Dict, Any

# Set up logging
logger = logging.getLogger("app.services.tire")

# ensure upload directory exists
UPLOAD_DIR = os.path.join("app", "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# load model & class indices once
MODEL_PATH = os.path.join("models", "hybrid_model.h5")
CLASS_INDICES_PATH = os.path.join("models", "class_indices.json")

# Initialize model and class_indices as None
model = None
idx_to_class = {}

try:
    logger.info(f"Loading model from {MODEL_PATH}")
    if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 0:
        model = tf.keras.models.load_model(MODEL_PATH)
        logger.info("Model loaded successfully")
    else:
        logger.error(f"Model file does not exist or is empty: {MODEL_PATH}")
        
    logger.info(f"Loading class indices from {CLASS_INDICES_PATH}")
    if os.path.exists(CLASS_INDICES_PATH):
        with open(CLASS_INDICES_PATH, "r") as f:
            class_indices = json.load(f)
        idx_to_class = {v: k for k, v in class_indices.items()}
        logger.info(f"Class indices loaded: {class_indices}")
    else:
        logger.error(f"Class indices file does not exist: {CLASS_INDICES_PATH}")
        # Create a default class indices file
        class_indices = {"good": 0, "defective": 1}
        idx_to_class = {0: "good", 1: "defective"}
        os.makedirs(os.path.dirname(CLASS_INDICES_PATH), exist_ok=True)
        with open(CLASS_INDICES_PATH, "w") as f:
            json.dump(class_indices, f, indent=2)
        logger.info(f"Created default class indices file: {class_indices}")
except Exception as e:
    logger.error(f"Error loading model or class_indices: {e}")
    # Provide fallback values for class_indices
    idx_to_class = {0: "good", 1: "defective"}

def estimate_fuel_consumption(rul_percentage: float) -> Dict[str, Any]:
    """
    Estimates fuel consumption based on the remaining useful life (RUL) percentage
    using interpolation between reference points.
    
    Args:
        rul_percentage (float): The calculated RUL percentage.
    
    Returns:
        Dict[str, Any]: A dictionary containing fuel consumption data.
    """
    # Reference points from the UMTRI-2014-1 study
    reference_points = {
        100: 505,  # Best case (New Tire)
        90: 517,
        75: 524,
        50: 529,  # Median case
        25: 536,
        10: 539,
        0: 547   # Worst case (Worn Tire)
    }
    
    rul_percentage = max(0, min(100, rul_percentage))
    sorted_points = sorted(reference_points.keys())
    
    # Calculate estimated consumption through interpolation
    if rul_percentage in reference_points:
        estimated_consumption = reference_points[rul_percentage]
    else:
        for i, point in enumerate(sorted_points):
            if point > rul_percentage:
                higher_point = point
                lower_point = sorted_points[i-1]
                break
        else:
            higher_point = 100
            lower_point = 0
        
        higher_consumption = reference_points[higher_point]
        lower_consumption = reference_points[lower_point]
        weight = (rul_percentage - lower_point) / (higher_point - lower_point)
        estimated_consumption = lower_consumption + weight * (higher_consumption - lower_consumption)
    
    # Constants from the study
    consumption_new_tire = reference_points[100]
    consumption_worn_tire = reference_points[0]
    price_per_gallon = 3.50
    
    # Calculate cost differences
    annual_extra_cost_vs_new = (estimated_consumption - consumption_new_tire) * price_per_gallon
    annual_potential_savings_vs_worn = (consumption_worn_tire - estimated_consumption) * price_per_gallon
    
    # Return data structure
    result = {
        "rul_percentage": rul_percentage,
        "estimated_annual_consumption": round(estimated_consumption, 1),
        "consumption_new_tire": consumption_new_tire,
        "consumption_worn_tire": consumption_worn_tire,
        "annual_extra_cost_vs_new": round(annual_extra_cost_vs_new, 2),
        "annual_potential_savings_vs_worn": round(annual_potential_savings_vs_worn, 2),
        "disclaimer": "Fuel consumption estimates based on UMTRI-2014-1 study figures for rolling resistance extremes. Actual consumption depends on vehicle, driving style, and conditions."
    }
    
    return result

async def save_and_analyze(file, db: AsyncSession) -> TireRecord:
    try:
        # If model is not loaded, use a default good value of 75%
        if model is None:
            logger.warning("Model not loaded, using default RUL value of 75%")
            rul_percent = 75
            
            # Save file to disk
            ext = file.filename.rsplit('.', 1)[-1]
            name = f"{uuid.uuid4().hex}.{ext}"
            path = os.path.join(UPLOAD_DIR, name)
            data = await file.read()
            with open(path, 'wb') as f:
                f.write(data)
                
            # Calculate fuel consumption data 
            try:
                fuel_data = estimate_fuel_consumption(rul_percent)
            except Exception as e:
                logger.error(f"Error calculating fuel consumption: {e}")
                fuel_data = None  # Fall back to None if calculation fails
            
            # Persist record in DB
            record = TireRecord(filename=name, rul_percent=rul_percent, fuel_data=fuel_data)
            db.add(record)
            await db.commit()
            await db.refresh(record)
            return record
        
        # Save file to disk
        ext = file.filename.rsplit('.', 1)[-1]
        name = f"{uuid.uuid4().hex}.{ext}"
        path = os.path.join(UPLOAD_DIR, name)
        data = await file.read()
        with open(path, 'wb') as f:
            f.write(data)

        # Preprocess for both branches
        img = cv2.imread(path)
        if img is None:
            logger.error(f"Failed to read image at {path}")
            raise RuntimeError(f"Failed to read image at {path}")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))

        # Custom branch input: normalized [0,1]
        custom_input = img.astype(np.float32) / 255.0
        custom_input = np.expand_dims(custom_input, axis=0)

        # ResNet50 branch input: ImageNet preprocessing
        resnet_input = tf.keras.applications.resnet50.preprocess_input(img.astype(np.float32))
        resnet_input = np.expand_dims(resnet_input, axis=0)

        # Run inference with both inputs
        logger.info("Running model inference")
        preds = model.predict([custom_input, resnet_input])

        # Extract good-tire probability
        good_idx = next((i for i, c in idx_to_class.items() if c == 'good'), 0)
        good_prob = float(preds[0][good_idx])
        rul_percent = int(round(good_prob * 100))
        logger.info(f"Prediction result: RUL={rul_percent}%")

        # Calculate fuel consumption data 
        try:
            fuel_data = estimate_fuel_consumption(rul_percent)
        except Exception as e:
            logger.error(f"Error calculating fuel consumption: {e}")
            fuel_data = None  # Fall back to None if calculation fails

        # Persist record in DB
        record = TireRecord(filename=name, rul_percent=rul_percent, fuel_data=fuel_data)
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record
    except Exception as e:
        logger.error(f"Error in save_and_analyze: {e}")
        # Make sure to rollback the session in case of error
        await db.rollback()
        raise
