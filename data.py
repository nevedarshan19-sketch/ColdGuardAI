from __future__ import annotations
import numpy as np
import pandas as pd

FEATURES = [
    "temperature", "humidity", "door_open", "compressor_on",
    "ambient_temperature", "minutes_since_maintenance", "temp_rate_5m"
]

def generate_synthetic_data(rows: int = 2500, seed: int = 42) -> pd.DataFrame:
    """Generate clearly synthetic, minute-level sensor data with future-excursion labels."""
    rng = np.random.default_rng(seed)
    t = pd.date_range("2026-01-01", periods=rows, freq="min")
    ambient = 24 + 5*np.sin(np.arange(rows)/180) + rng.normal(0, 1.2, rows)
    temp = np.zeros(rows)
    temp[0] = 4.0
    humidity = np.zeros(rows)
    door = rng.binomial(1, 0.035, rows)
    compressor = np.ones(rows, dtype=int)
    maintenance = np.zeros(rows)
    for i in range(rows):
        if i > 0:
            compressor[i] = 0 if (rng.random() < 0.035) else (1 if temp[i-1] > 5.0 else int(compressor[i-1]))
            drift = 0.025 if door[i] else 0.0
            warming = 0.055 if not compressor[i] else -0.035
            temp[i] = temp[i-1] + warming + drift + 0.012*(ambient[i]-24) + rng.normal(0, 0.09)
            # Occasional realistic-looking synthetic disturbances, not real sensor records.
            if rng.random() < 0.008:
                temp[i] += rng.uniform(0.4, 1.5)
            temp[i] = np.clip(temp[i], -1.0, 14.0)
        humidity[i] = np.clip(67 + 7*door[i] + rng.normal(0, 5), 25, 98)
        maintenance[i] = min(i % 1000, 1000)
    s = pd.Series(temp)
    rate = s.diff(5).fillna(0).to_numpy() / 5.0
    df = pd.DataFrame({
        "timestamp": t,
        "temperature": temp,
        "humidity": humidity,
        "door_open": door,
        "compressor_on": compressor,
        "ambient_temperature": ambient,
        "minutes_since_maintenance": maintenance,
        "temp_rate_5m": rate,
    })
    # Label each row from the maximum temperature in the NEXT 30 minutes.
    future_max = s.shift(-1).rolling(30, min_periods=30).max().shift(-29)
    # Equivalent robust future-window calculation.
    values = s.to_numpy()
    labels = np.zeros(rows, dtype=int)
    for i in range(rows - 30):
        labels[i] = int(np.max(values[i+1:i+31]) > 8.0)
    df["future_excursion_30m"] = labels
    df = df.iloc[:-30].reset_index(drop=True)
    return df

def validate_sensor_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Validate uploaded CSV columns and return a cleaned copy plus warnings."""
    required = ["timestamp", "temperature", "humidity"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError("CSV is missing required column(s): " + ", ".join(missing))
    out = df.copy()
    warnings = []
    out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    out["temperature"] = pd.to_numeric(out["temperature"], errors="coerce")
    out["humidity"] = pd.to_numeric(out["humidity"], errors="coerce")
    invalid = out[["timestamp", "temperature", "humidity"]].isna().any(axis=1)
    if invalid.any():
        warnings.append(f"Removed {int(invalid.sum())} row(s) with missing or invalid required values.")
        out = out.loc[~invalid].copy()
    if "door_open" not in out: out["door_open"] = 0
    if "compressor_on" not in out: out["compressor_on"] = 1
    if "ambient_temperature" not in out: out["ambient_temperature"] = 24.0
    if "minutes_since_maintenance" not in out: out["minutes_since_maintenance"] = 0.0
    for c in ["door_open", "compressor_on", "ambient_temperature", "minutes_since_maintenance"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
        out[c] = out[c].fillna(0 if c != "compressor_on" else 1)
    out = out.sort_values("timestamp").reset_index(drop=True)
    out["temp_rate_5m"] = out["temperature"].diff(5).fillna(0) / 5.0
    spikes = (out["temperature"].diff().abs() > 3.0).sum()
    if spikes:
        warnings.append(f"Flagged {int(spikes)} possible abrupt temperature spike(s) (>3°C in one reading).")
    if len(out) and (out["temperature"].min() < -50 or out["temperature"].max() > 60):
        warnings.append("Temperature includes values outside a broad plausibility range (-50°C to 60°C). Review sensor units.")
    return out, warnings
