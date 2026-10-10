from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from coldguard.data import generate_synthetic_data

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "sample_sensor_data.csv"
    df = generate_synthetic_data(rows=3000)
    df.to_csv(out, index=False)
    print(f"Created SYNTHETIC demo dataset: {out} ({len(df)} rows)")
