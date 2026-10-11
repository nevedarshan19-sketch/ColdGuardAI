from __future__ import annotations
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
from data import FEATURES, generate_synthetic_data

class ColdGuardModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=140, max_depth=9, min_samples_leaf=4,
            class_weight="balanced", random_state=42, n_jobs=-1
        )
        self.trained = False
        self.metrics = {}

    def train(self, df: pd.DataFrame | None = None):
        df = df if df is not None else generate_synthetic_data()
        # Chronological split: earlier records train, later records test.
        split = int(len(df) * 0.8)
        train, test = df.iloc[:split], df.iloc[split:]
        X_train = train[FEATURES].fillna(0)
        y_train = train["future_excursion_30m"].astype(int)
        X_test = test[FEATURES].fillna(0)
        y_test = test["future_excursion_30m"].astype(int)
        self.model.fit(X_train, y_train)
        pred = self.model.predict(X_test)
        tn, fp, fn, tp = confusion_matrix(y_test, pred, labels=[0,1]).ravel()
        self.metrics = {
            "precision": float(precision_score(y_test, pred, zero_division=0)),
            "recall": float(recall_score(y_test, pred, zero_division=0)),
            "f1": float(f1_score(y_test, pred, zero_division=0)),
            "false_alarm_rate": float(fp / (fp + tn)) if fp + tn else 0.0,
            "test_rows": int(len(test)),
            "test_positive_rate": float(y_test.mean()),
            "note": "Metrics are from a synthetic chronological holdout only; they are not real-world validation."
        }
        self.trained = True
        return self.metrics

    def predict_probability(self, row: dict) -> float:
        if not self.trained:
            self.train()
        x = pd.DataFrame([{k: row.get(k, 0) for k in FEATURES}])[FEATURES].fillna(0)
        probs = self.model.predict_proba(x)[0]
        classes = list(self.model.classes_)
        return float(probs[classes.index(1)]) if 1 in classes else 0.0

    def feature_importance(self) -> pd.DataFrame:
        if not self.trained: self.train()
        return pd.DataFrame({"feature": FEATURES, "importance": self.model.feature_importances_}).sort_values("importance", ascending=True)
