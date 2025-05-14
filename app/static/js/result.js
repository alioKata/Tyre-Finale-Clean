document.addEventListener("DOMContentLoaded", async () => {
    const chartEl = document.getElementById("resultChart");
    const percEl = document.getElementById("resultPercentage");
    const nextUpEl = document.getElementById("nextUploadDate");
    const newBtn = document.getElementById("newUploadButton");
    const fileInput = document.getElementById("newFileInput");
    const backBtn = document.getElementById("backButton");
    const extraCostEl = document.getElementById("extraCostVsNew");
    const savingsEl = document.getElementById("potentialSavingsVsWorn");

    const token = localStorage.getItem("token");
    if (!token) {
        return window.location.href = "/login";
    }
    const authHeader = { "Authorization": `Bearer ${token}` };

    let record;
    try {
        const res = await fetch("/api/tire/latest", { headers: authHeader });
        if (!res.ok) throw new Error("No previous record");
        record = await res.json();
    } catch {
        nextUpEl.textContent = "No previous submission.";
        percEl.textContent = "--%";
        return;
    }

    const rul = record.rul_percent;
    const angle = (rul / 100) * 360;
    chartEl.style.background =
        `conic-gradient(#1877f2 0deg ${angle}deg, #ccc ${angle}deg 360deg)`;
    percEl.textContent = `${rul}%`;

    const uploadDate = new Date(record.upload_time);
    const nextDate = new Date(uploadDate);
    nextDate.setMonth(nextDate.getMonth() + 2);
    nextUpEl.textContent =
        `Next upload is on: ${nextDate.toLocaleDateString(undefined, {
            year: "numeric", month: "long", day: "numeric"
        })}`;

    const fuelData = calculateFuelData(rul);

    extraCostEl.textContent =
        `Annual Extra Cost vs. New Tire: $${fuelData.annual_extra_cost_vs_new.toFixed(2)}`;
    savingsEl.textContent =
        `Potential Savings vs. Worn Tire: $${fuelData.annual_potential_savings_vs_worn.toFixed(2)}`;

    createFuelConsumptionChart(fuelData);

    newBtn.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const alertDiv = document.createElement("div");
        alertDiv.className = "processing-alert";
        alertDiv.innerHTML = `
      <div class="alert-content">
        <p>Processing your image... please wait.</p>
        <div class="spinner"><span class="gear">⚙️</span></div>
      </div>`;
        document.body.appendChild(alertDiv);

        const form = new FormData();
        form.append("file", file);
        try {
            const res2 = await fetch("/api/tire/upload", {
                method: "POST",
                headers: authHeader,
                body: form
            });
            if (!res2.ok) {
                const err = await res2.json();
                throw new Error(err.detail || "Upload failed");
            }
            setTimeout(() => window.location.reload(), 1000);
        } catch (err) {
            alert("Error: " + err.message);
            alertDiv.remove();
        }
    });

    backBtn.addEventListener("click", () => {
        window.location.href = "/";
    });
});

function calculateFuelData(rul_percentage) {
    const reference_points = {
        100: 505,  // Best case (New Tire)
        90: 517,
        75: 524,
        50: 529,  // Median case
        25: 536,
        10: 539,
        0: 547   // Worst case (Worn Tire)
    };

    rul_percentage = Math.max(0, Math.min(100, rul_percentage));

    let estimated_consumption;
    if (reference_points[rul_percentage] !== undefined) {
        estimated_consumption = reference_points[rul_percentage];
    } else {
        const sorted_points = Object.keys(reference_points)
            .map(Number)
            .sort((a, b) => a - b);

        let higher_point = 100;
        let lower_point = 0;

        for (let i = 0; i < sorted_points.length; i++) {
            if (sorted_points[i] > rul_percentage) {
                higher_point = sorted_points[i];
                lower_point = sorted_points[i - 1];
                break;
            }
        }

        const higher_consumption = reference_points[higher_point];
        const lower_consumption = reference_points[lower_point];
        const range = higher_point - lower_point;

        if (range <= 0) {
            estimated_consumption = higher_consumption;
        } else {
            const weight = (rul_percentage - lower_point) / range;
            estimated_consumption = lower_consumption + weight * (higher_consumption - lower_consumption);
        }
    }

    const next_year_rul = Math.max(0, rul_percentage - 25);
    let next_year_consumption;

    if (reference_points[next_year_rul] !== undefined) {
        next_year_consumption = reference_points[next_year_rul];
    } else {
        const sorted_points = Object.keys(reference_points)
            .map(Number)
            .sort((a, b) => a - b);

        let higher_point = 100;
        let lower_point = 0;

        for (let i = 0; i < sorted_points.length; i++) {
            if (sorted_points[i] > next_year_rul) {
                higher_point = sorted_points[i];
                lower_point = sorted_points[i - 1];
                break;
            }
        }

        const higher_consumption = reference_points[higher_point];
        const lower_consumption = reference_points[lower_point];
        const range = higher_point - lower_point;

        if (range <= 0) {
            next_year_consumption = higher_consumption;
        } else {
            const weight = (next_year_rul - lower_point) / range;
            next_year_consumption = lower_consumption + weight * (higher_consumption - lower_consumption);
        }
    }

    const consumption_new_tire = reference_points[100];
    const consumption_worn_tire = reference_points[0];
    const price_per_gallon = 3.50;

    const annual_extra_cost_vs_new = (estimated_consumption - consumption_new_tire) * price_per_gallon;
    const annual_potential_savings_vs_worn = (consumption_worn_tire - estimated_consumption) * price_per_gallon;

    estimated_consumption = Math.round(estimated_consumption * 10) / 10;
    next_year_consumption = Math.round(next_year_consumption * 10) / 10;

    return {
        rul_percentage: rul_percentage,
        next_year_rul: next_year_rul,
        estimated_annual_consumption: estimated_consumption,
        next_year_consumption: next_year_consumption,
        consumption_new_tire: consumption_new_tire,
        consumption_worn_tire: consumption_worn_tire,
        annual_extra_cost_vs_new: Math.round(annual_extra_cost_vs_new * 100) / 100,
        annual_potential_savings_vs_worn: Math.round(annual_potential_savings_vs_worn * 100) / 100
    };
}

function createFuelConsumptionChart(fuelData) {
    const canvas = document.getElementById('fuelConsumptionChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const currentYearConsumption = fuelData.estimated_annual_consumption;
    const nextYearConsumption = fuelData.next_year_consumption;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Current Year', 'Next Year (Estimated)'],
            datasets: [{
                label: 'Annual Fuel Consumption (Gallons)',
                data: [currentYearConsumption, nextYearConsumption],
                backgroundColor: ['#1877f2', '#ff9800'],
                borderColor: ['#0a5dc2', '#e65100'],
                borderWidth: 1,
                barThickness: 70
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.parsed.y.toFixed(1)} gallons per year`;
                        },
                        afterLabel: function (context) {
                            if (context.dataIndex === 0) {
                                return `RUL: ${fuelData.rul_percentage}%`;
                            } else {
                                return `Estimated RUL: ${fuelData.next_year_rul}%`;
                            }
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: Math.min(currentYearConsumption, nextYearConsumption) - 5,
                    title: {
                        display: true,
                        text: 'Gallons per Year',
                        font: {
                            weight: 'bold'
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time Period',
                        font: {
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
} 
