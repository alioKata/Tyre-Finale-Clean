#!/bin/bash 
mkdir -p models 
curl -L -o models/hybrid_model.h5 https://your-aws-s3-url/hybrid_model.h5 
chmod +x start.sh 
