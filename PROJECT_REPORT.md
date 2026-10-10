# ColdGuard AI — Project Report

## 1. Abstract

ColdGuard AI is an educational early-warning prototype for cold-storage monitoring. It combines sensor-like readings, feature engineering, a Random Forest classifier, transparent baseline rules, and an operator-facing dashboard. Instead of only notifying after a temperature threshold is crossed, it estimates whether an excursion may occur within a defined future window.

## 2. Problem statement

Medicines, vaccines and perishable food can be damaged when storage conditions move outside product-specific limits. Simple threshold alarms are useful for detecting current problems but do not necessarily provide advance warning. A predictive system may help staff investigate rising temperatures, open doors, or equipment interruptions sooner.

## 3. Proposed solution

ColdGuard AI demonstrates a data pipeline from simulated sensor readings or CSV uploads through validation and feature engineering to model inference and risk classification. It provides a dashboard, a persistent alert log, and downloadable reports.

## 4. Social impact

Earlier awareness may help operators respond faster, reduce avoidable product loss, and support more reliable cold-chain operations. The project is relevant to public health and food logistics, but these benefits are hypotheses that would need to be measured in a real pilot.

## 5. Architecture

1. Data input: synthetic simulator or CSV upload.
2. Validation: required columns, timestamp parsing, numeric checks and missing-value handling.
3. Feature engineering: rate of temperature change and equipment-state features.
4. Prediction: Random Forest classifier estimates future excursion probability.
5. Baseline: interpretable rules flag current excursions and concerning operating conditions.
6. Risk classification: low, medium or high based on configurable probability cutoffs.
7. Dashboard and storage: Streamlit pages and SQLite alert history.
8. Operator verification: acknowledge/resolve alerts and record notes.

## 6. Machine-learning methodology

- Algorithm: scikit-learn RandomForestClassifier.
- Features: temperature, humidity, door-open state, compressor state, ambient temperature, minutes since maintenance, and temperature rate of change.
- Target: any temperature above 8°C during the next 30 minutes.
- Data: generated synthetic minute-level time series.
- Split: chronological 80% training and 20% test, without shuffling.
- Metrics: precision, recall, F1 score and false-alarm rate on the synthetic holdout.

The model does not use future temperatures as input features. The target is derived from future temperatures, which is appropriate for supervised forecasting. The split is chronological, but because this is one synthetic sequence, the metrics are not evidence of real-world performance. Synthetic data may not capture real refrigeration dynamics, sensor errors, loading patterns, defrost cycles, or site-specific behaviour.

## 7. Current excursion versus predicted risk

A current excursion is a direct comparison of the latest temperature with the configured lower and upper limits. Predicted risk is a model estimate for a future window. These are shown separately so that an already-occurring excursion is not confused with a forecast.

## 8. Evaluation plan for a real pilot

1. Agree on product-specific operating limits with qualified stakeholders.
2. Collect calibrated temperature and relevant equipment data with reliable timestamps.
3. Define an excursion event and prediction horizon before evaluating.
4. Label outcomes independently and document missing data.
5. Split data by time and, where possible, hold out entire sites or storage units.
6. Compare the model against simple threshold and trend baselines.
7. Report precision, recall, F1, false alarms per day, missed events, and lead time before excursion.
8. Evaluate performance across seasons, door events, defrost cycles, and equipment types.
9. Keep a human operator in the loop; do not automate safety-critical decisions from this prototype.

## 9. Limitations

- All bundled training data and live-demo readings are synthetic.
- The model uses a fixed 8°C target label and 30-minute training horizon.
- Changing UI thresholds does not retrain the model.
- Feature importance is global model behaviour, not causal attribution for an individual prediction.
- Spike flags are simple heuristics; sensor drift is not formally diagnosed.
- No hardware sensor connection or external notification service is implemented.
- SQLite is local to the machine running the app and is not a multi-user production database.
- The application is not certified or validated for operational safety decisions.

## 10. Future improvements

- Integrate real IoT sensors through a secure MQTT or HTTPS gateway.
- Retrain on validated, site-specific historical data.
- Add drift detection based on calibration records and statistical monitoring.
- Add model calibration and uncertainty reporting.
- Add role-based access, audit logs, encrypted transport and backups.
- Add notifications only after delivery reliability and escalation paths are tested.
- Deploy with monitoring, versioned models, rollback, and human oversight.

## 11. Conclusion

ColdGuard AI demonstrates a complete beginner-level predictive-monitoring workflow and provides an interface for exploring risk, reviewing alerts and exporting data. The next engineering step is not simply a more complex model: it is collecting trustworthy data and validating performance against clearly defined real-world outcomes.
