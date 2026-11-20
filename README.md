# Campus Energy-Use Analyser

A Python-based analytical pipeline to inspect daily electricity-meter readings across campus buildings, flag abnormal or missing entries, compute moving averages, export monthly JSON summaries, and generate trend visualizations.

**Author:** Soham Saha (Roll No: 32 | Section: A | Enrollment No: 12025052003033)  
**Department:** Electronics and Communication Engineering, IEM Kolkata  
**Dataset Notice:** All readings in `simulated_campus_energy.csv` are **synthetically generated (SIMULATED)** for academic demonstration and do not represent real campus utility meters.

## Project Structure
- `generate_data.py` – Generates the clearly labelled simulated 90-day dataset (`simulated_campus_energy.csv`).
- `energy_analyser.py` – Main pipeline (CO1–CO6): validation functions, `MeterRecord` class, NumPy moving averages, Pandas monthly summaries & JSON export, BL5 rule comparison, and Matplotlib plots.
- `test_analyser.py` – Unit tests verifying validation logic, class special methods, and NumPy calculations.
- `outputs/` – Generated `monthly_summary.json` and PNG plots.
- `Campus_Energy_Use_Analyser_Report.pdf` – Final project report.

## Requirements
```bash
pip install numpy pandas matplotlib