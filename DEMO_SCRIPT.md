# ColdGuard AI — 3-Minute Hackathon Demo

## 0:00–0:25 — Problem
“Cold storage is important for vaccines, medicines and food. A conventional threshold alarm may only react after temperature has already moved outside its allowed range. Our idea is to estimate excursion risk in advance, so an operator has time to investigate.”

## 0:25–0:50 — Product
“This is ColdGuard AI. The dashboard shows current temperature and humidity, the estimated risk over the next 30 minutes, equipment state, and recent temperature history. This version runs locally and uses synthetic demo data.”

## 0:50–1:20 — Predictive logic
“The Random Forest uses temperature, humidity, door state, compressor state, ambient temperature, time since maintenance, and recent rate of temperature change. A separate rule-based baseline provides understandable checks. Current excursion detection is kept separate from predicted future risk.”

## 1:20–1:50 — Live simulation
“I’ll open the door and simulate a rising trend. The feature values and model estimate update. Now I’ll trigger a current excursion to show the difference between a prediction and an already out-of-range temperature.”

## 1:50–2:20 — Alerts and response
“I can record the risk assessment in the Alerts Centre, acknowledge it, and add an operator note. The alert history is stored in SQLite, so it remains available after refreshing or restarting the app on this machine.”

## 2:20–2:40 — Data and reports
“We can upload a historical CSV, validate its required fields, flag abrupt spikes, and download a cleaned file or report. The report also shows basic synthetic holdout metrics.”

## 2:40–3:00 — Impact and honesty
“Our intended impact is faster awareness and reduced avoidable loss. The current dataset is synthetic, so the displayed metrics do not establish real-world accuracy. A real pilot needs calibrated sensors, product-specific limits, independently labelled data, reliability testing and human oversight.”

## Before presenting
- Start the app and open Overview.
- Keep the sample CSV ready at `data/sample_sensor_data.csv`.
- Trigger one excursion and create an alert before opening the Alerts Centre.
- Avoid claiming the model has been validated in a real cold-storage facility.
- If the model risk is low during the demo, use “Trigger excursion” to demonstrate current excursion detection and alert logging.

## Likely judge questions

**Q: What is actually AI about this?**  
A: A Random Forest classifier learns patterns from labelled historical feature rows to estimate the probability of an excursion in a future window. The baseline rules are separate and interpretable.

**Q: How accurate is it?**  
A: The app calculates precision, recall, F1 and false-alarm rate on a chronological holdout from synthetic data. Those metrics only test the software pipeline; they are not a real-world performance claim. We need labelled facility data for meaningful validation.

**Q: Why not use only a threshold alarm?**  
A: Threshold alarms remain important for current excursions. The predictive layer adds a risk estimate based on trend and operating context, potentially providing earlier warning.

**Q: How do you avoid data leakage?**  
A: Future readings are used only to create the target label, not as model inputs. The data is split chronologically rather than randomly shuffled.

**Q: Can it be used for vaccine storage now?**  
A: No. This is a prototype. Operational use requires validated sensors, calibration, product-specific limits, reliability testing, security and human oversight.

**Q: What is the next step?**  
A: Work with a cold-chain operator to collect calibrated readings and verified excursion labels, then compare the model against threshold and trend baselines using false alarms per day, missed events and lead time.
