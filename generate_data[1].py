import csv
import random
from datetime import date, timedelta

def generate_simulated_dataset(filename="simulated_campus_energy.csv"):
    random.seed(42)
    start_date = date(2026, 8, 1)
    num_days = 90

    # Building metadata: base daily kWh and normal daily variation
    buildings = {
        "Academic_Block_A": {"base": 450.0, "std": 35.0},
        "Hostel_Block_B":   {"base": 320.0, "std": 25.0},
        "Lab_Complex_C":    {"base": 600.0, "std": 50.0},
    }

    rows = []
    for day_offset in range(num_days):
        current_date = start_date + timedelta(days=day_offset)
        is_weekend = current_date.weekday() >= 5

        for bldg, params in buildings.items():
            # Simulate lower usage on weekends for Academic/Lab, higher for Hostel
            modifier = 0.85 if (is_weekend and bldg != "Hostel_Block_B") else 1.0
            if is_weekend and bldg == "Hostel_Block_B":
                modifier = 1.12

            kwh = round(random.gauss(params["base"] * modifier, params["std"]), 2)

            # Inject a realistic multi-day event spike (e.g., mid-sem lab exams)
            if bldg == "Lab_Complex_C" and 40 <= day_offset <= 43:
                kwh = round(kwh * 1.45, 2)

            rows.append({
                "date": current_date.isoformat(),
                "building": bldg,
                "kwh_reading": kwh,
                "data_source": "SIMULATED"
            })

    # Inject intentional anomalies / corrupt records for BL4 analysis:
    # 1. Negative meter reading (sensor/reset error)
    rows[15]["kwh_reading"] = -45.5
    rows[110]["kwh_reading"] = -12.0
    # 2. Missing reading (blank / incomplete data)
    rows[64]["kwh_reading"] = ""
    rows[185]["kwh_reading"] = ""
    # 3. Extreme single-day glitch spike (meter malfunction)
    rows[200]["kwh_reading"] = 2450.0

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "building", "kwh_reading", "data_source"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Simulated dataset saved to '{filename}' ({len(rows)} rows).")

if __name__ == "__main__":
    generate_simulated_dataset()