
import csv
import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ==============================================================================
# CO1: Procedural Control Flow & Functions (Validation & Anomaly Flagging)
# ==============================================================================
def validate_reading(raw_value, max_threshold=1200.0):
    """
    Validates a single meter reading.
    Returns (cleaned_float_or_None, status_flag).
    """
    if raw_value is None or str(raw_value).strip() == "":
        return None, "MISSING"
    try:
        val = float(raw_value)
    except ValueError:
        return None, "INVALID_FORMAT"

    if val < 0:
        return val, "NEGATIVE_ERROR"
    if val > max_threshold:
        return val, "ABNORMAL_SPIKE"
    return val, "VALID"


def compute_moving_average(values_array, window=7):
    """CO4: Computes a NumPy moving average over valid (non-NaN) readings."""
    if len(values_array) < window:
        return np.array([])
    kernel = np.ones(window) / window
    # Replace NaN with series median before convolution so gaps don't break the curve
    clean_arr = np.where(np.isnan(values_array), np.nanmedian(values_array), values_array)
    return np.convolve(clean_arr, kernel, mode="valid")


# ==============================================================================
# CO3: Class with Relevant Special Methods (_init, __len, __getitem, ___iter__)
# ==============================================================================
class MeterRecord:
    """
    Encapsulates daily electricity-meter readings for a single campus building.
    Implements _len, __getitem, and ___iter__ so building records can be
    inspected, sliced, and iterated over directly like native Python containers.
    """

    def __init__(self, building_name):
        self.building_name = building_name
        self.records = []  # List of dicts: {"date", "kwh", "status"}

    def add_reading(self, date_str, raw_value, max_threshold=1200.0):
        val, status = validate_reading(raw_value, max_threshold)
        self.records.append({"date": date_str, "kwh": val, "status": status})

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        return self.records[index]

    def __iter__(self):
        return iter(self.records)

    def __repr__(self):
        return f"MeterRecord(building='{self.building_name}', entries={len(self)})"

    def valid_values_array(self):
        """CO4: Returns a NumPy array of valid kWh readings (NaN for invalid/missing)."""
        vals = [
            r["kwh"] if r["status"] == "VALID" else np.nan
            for r in self.records
        ]
        return np.array(vals, dtype=float)

    def anomaly_summary(self):
        """Counts each type of flagged anomaly for BL4 failure-case analysis."""
        counts = {"MISSING": 0, "NEGATIVE_ERROR": 0, "ABNORMAL_SPIKE": 0, "INVALID_FORMAT": 0}
        for r in self.records:
            if r["status"] in counts:
                counts[r["status"]] += 1
        return counts


# ==============================================================================
# CO2: Data Structures & File I/O (Load CSV into Dict of MeterRecord Objects)
# ==============================================================================
def load_building_records(csv_path, max_threshold=1200.0):
    """Reads CSV file and returns a dictionary mapping building_name -> MeterRecord."""
    buildings = {}
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bldg = row["building"]
            if bldg not in buildings:
                buildings[bldg] = MeterRecord(bldg)
            buildings[bldg].add_reading(row["date"], row["kwh_reading"], max_threshold)
    return buildings


# ==============================================================================
# BL5: Evaluate Anomaly Rule (Fixed Threshold vs. Statistical Z-Score Rule)
# ==============================================================================
def evaluate_anomaly_rules(buildings, fixed_threshold=1200.0, z_cutoff=2.5):
    """
    Compares two spike-detection rules:
      Rule A: Fixed Threshold (> 1200 kWh)
      Rule B: Statistical Z-Score (|z| > 2.5 per building)
    """
    evaluation = {}
    for name, meter in buildings.items():
        # Extract all numeric non-negative readings to test spike detection
        numeric_vals = np.array([
            r["kwh"] for r in meter if r["kwh"] is not None and r["kwh"] >= 0
        ], dtype=float)

        mean_val = np.mean(numeric_vals)
        std_val = np.std(numeric_vals)

        fixed_flags = int(np.sum(numeric_vals > fixed_threshold))
        z_scores = (numeric_vals - mean_val) / (std_val if std_val > 0 else 1.0)
        z_flags = int(np.sum(np.abs(z_scores) > z_cutoff))

        evaluation[name] = {
            "mean_kwh": round(float(mean_val), 2),
            "std_kwh": round(float(std_val), 2),
            "fixed_rule_spikes": fixed_flags,
            "zscore_rule_spikes": z_flags,
        }
    return evaluation


# ==============================================================================
# CO5: Pandas Monthly Summaries & JSON Export
# ==============================================================================
def build_pandas_summary_and_export(csv_path, json_output_path):
    """Uses Pandas DataFrames to compute monthly building summaries and export JSON."""
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df["kwh_numeric"] = pd.to_numeric(df["kwh_reading"], errors="coerce")

    # Keep only valid non-negative readings <= 1200 for clean monthly aggregation
    clean_df = df[(df["kwh_numeric"] >= 0) & (df["kwh_numeric"] <= 1200)].copy()
    clean_df["month"] = clean_df["date"].dt.to_period("M").astype(str)

    monthly = (
        clean_df.groupby(["month", "building"])["kwh_numeric"]
        .agg(total_kwh="sum", avg_daily_kwh="mean", max_daily_kwh="max", valid_days="count")
        .round(2)
        .reset_index()
    )

    summary_dict = monthly.to_dict(orient="records")
    with open(json_output_path, mode="w", encoding="utf-8") as f:
        json.dump(summary_dict, f, indent=2)

    return clean_df, monthly


# ==============================================================================
# CO6: Matplotlib Plots (At least two well-labelled plots)
# ==============================================================================
def generate_plots(buildings, monthly_df, output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)

    # Plot 1: Daily Usage Trends + 7-Day Moving Average per Building
    plt.figure(figsize=(11, 5))
    for name, meter in buildings.items():
        vals = meter.valid_values_array()
        ma7 = compute_moving_average(vals, window=7)
        days = np.arange(len(vals))
        plt.plot(days, vals, alpha=0.3, linewidth=1)
        plt.plot(days[6:], ma7, linewidth=2.2, label=f"{name} (7-day MA)")

    plt.title("Simulated Campus Electricity Usage Trends (with 7-Day Moving Average)")
    plt.xlabel("Day Index (Aug–Oct 2026)")
    plt.ylabel("Electricity Consumption (kWh)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plot1_path = os.path.join(output_dir, "plot_daily_trends.png")
    plt.savefig(plot1_path, dpi=150)
    plt.close()

    # Plot 2: Monthly Total Energy Comparison by Building (Grouped Bar Chart)
    pivot_df = monthly_df.pivot(index="month", columns="building", values="total_kwh")
    ax = pivot_df.plot(kind="bar", figsize=(9, 5))
    ax.set_title("Monthly Total Electricity Consumption by Building (Simulated Data)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Consumption (kWh)")
    ax.legend(title="Building")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plot2_path = os.path.join(output_dir, "plot_monthly_comparison.png")
    plt.savefig(plot2_path, dpi=150)
    plt.close()

    print(f"[OK] Plots saved to '{plot1_path}' and '{plot2_path}'.")


# ==============================================================================
# Main Execution Pipeline
# ==============================================================================
def main():
    csv_file = "simulated_campus_energy.csv"
    os.makedirs("outputs", exist_ok=True)
    json_out = os.path.join("outputs", "monthly_summary.json")

    if not os.path.exists(csv_file):
        print(f"[ERROR] '{csv_file}' not found. Run 'python generate_data.py' first.")
        return

    print("=== CAMPUS ENERGY-USE ANALYSER (SIMULATED DATASET) ===\n")

    # CO2 & CO3: Load data into MeterRecord objects
    buildings = load_building_records(csv_file)
    for name, meter in buildings.items():
        vals = meter.valid_values_array()
        total_kwh = np.nansum(vals)
        mean_kwh = np.nanmean(vals)
        anomalies = meter.anomaly_summary()
        print(f"{meter}")
        print(f"  Total Valid Usage : {total_kwh:,.2f} kWh | Daily Mean: {mean_kwh:.2f} kWh")
        print(f"  Flagged Anomalies : {anomalies}\n")

    # BL5: Compare anomaly detection rules
    print("--- BL5 Evaluation: Fixed Threshold (>1200 kWh) vs. Z-Score (|z| > 2.5) ---")
    eval_results = evaluate_anomaly_rules(buildings)
    for bldg, stats in eval_results.items():
        print(f"  {bldg}: {stats}")

    # CO5: Pandas summary & JSON export
    _, monthly_df = build_pandas_summary_and_export(csv_file, json_out)
    print(f"\n[OK] Monthly summary exported to '{json_out}'.")
    print("\nMonthly Summary Table:")
    print(monthly_df.to_string(index=False))

    # CO6: Generate Matplotlib plots
    generate_plots(buildings, monthly_df, output_dir="outputs")


if __name__ == "__main__":
    main()