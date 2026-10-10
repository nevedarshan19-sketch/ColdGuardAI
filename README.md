# ColdGuard AI

**AI-Based Predictive Cold-Storage Excursion & Early-Warning System**  
VIT CodeApex · Track 4: Technology for Social Impact

ColdGuard AI is a beginner-friendly Streamlit prototype that combines a Random Forest classifier with transparent baseline rules to demonstrate early warning for potential cold-storage temperature excursions.

> **Safety notice:** This is an educational prototype. It is not certified, calibrated, or validated for medicine, vaccine, food, or other operational safety decisions. All generated data and demo results are synthetic. Real deployment requires validated sensors, calibration, product-specific limits, reliability testing, and qualified human oversight.

## Features

- Streamlit dashboard with Overview, Predictive Analytics, Alerts Centre, Sensor Monitoring, Reports and Settings.
- Random Forest probability estimate for a future temperature excursion.
- Rule-based checks to provide readable warning reasons.
- Synthetic training data generated at startup.
- Chronological train/test split and precision, recall, F1, false-alarm rate.
- CSV upload validation, missing-value handling, spike flagging, cleaned CSV download.
- SQLite-backed alert history with acknowledge/resolve actions.
- Interactive demo controls and downloadable CSV reports.

## Architecture

Sensor/demo input or CSV → validation → feature engineering → Random Forest prediction + baseline rules → risk classification → dashboard and SQLite alert log → operator verification.

## Requirements

- macOS, Windows or Linux
- Python 3.10–3.12 recommended
- Internet is needed once to install packages. No paid API is used.

## Run on macOS

1. Download and unzip the project.
2. Open Terminal.
3. Change directory into the project folder. Example if it is in Downloads:

   ```bash
   cd ~/Downloads/ColdGuardAI
   ```

4. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

5. Activate it:

   ```bash
   source .venv/bin/activate
   ```

6. Upgrade pip and install packages:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. Launch the dashboard:

   ```bash
   streamlit run app.py
   ```

8. Streamlit will print a local URL, usually `http://localhost:8501`. Open it in your browser.

To stop the app, return to Terminal and press `Control + C`.

## Generate the sample dataset

With the virtual environment active:

```bash
python data/generate_dataset.py
```

This creates `data/sample_sensor_data.csv`. The records are synthetic and must be labelled as such in any presentation.

## Quick demo checklist

1. Open Overview and point out the current temperature, risk estimate and prediction horizon.
2. Toggle Door open and Compressor on/off.
3. Increase the temperature or click **Trigger excursion**.
4. Click **Log current risk assessment** in Alerts Centre; acknowledge and resolve it with an operator note.
5. Upload `data/sample_sensor_data.csv` under Sensor Monitoring.
6. Download a sensor report under Reports.
7. Reset demo controls.

## CSV format

Required columns:

- `timestamp` — parseable date/time
- `temperature` — numeric temperature in °C
- `humidity` — numeric relative humidity

Optional columns:

- `door_open` — 0 or 1
- `compressor_on` — 0 or 1
- `ambient_temperature`
- `minutes_since_maintenance`

Extra columns are preserved where practical, but only the supported feature fields are used by the model.

## Model methodology

The target label is whether any temperature in the next 30 minutes exceeds 8°C. The model uses current temperature, humidity, door state, compressor state, ambient temperature, time since maintenance, and recent temperature rate of change. The training data is synthetic. A chronological 80/20 split is used to avoid random shuffling across time.

The Settings page can change displayed operating limits, but the starter model's training label is fixed at 8°C and 30 minutes. Changing settings does not retrain the model. For a real experiment, generate labels using the chosen product-specific threshold and horizon, then retrain and re-evaluate.

## Troubleshooting

**`python3: command not found`**  
Install Python 3 from python.org or use the Python installation supplied by your development environment. On some Macs, `python3` may already be available.

**`streamlit: command not found`**  
Activate the environment with `source .venv/bin/activate`, then run `python -m pip install -r requirements.txt`. You can also launch with `python -m streamlit run app.py`.

**Package installation fails**  
Check your internet connection and Python version (`python3 --version`). Recreate the virtual environment if necessary.

**Port 8501 is busy**  
Run `streamlit run app.py --server.port 8502`.

**Uploaded CSV says a column is missing**  
Ensure it contains `timestamp`, `temperature`, and `humidity`. Check spelling and that temperature values are numeric.

**Dashboard says synthetic data**  
That is intentional. Do not present synthetic metrics as field-validated results.

## File guide

- `app.py`: dashboard and demo controls.
- `coldguard/data.py`: synthetic data generation and CSV validation.
- `coldguard/model.py`: Random Forest training, prediction and metrics.
- `coldguard/storage.py`: SQLite alert storage.
- `data/generate_dataset.py`: exports a sample CSV.
- `PROJECT_REPORT.md`: project report and limitations.
- `DEMO_SCRIPT.md`: presentation plan and judge Q&A.
- `architecture.mmd`: editable architecture diagram.
