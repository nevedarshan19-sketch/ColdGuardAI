from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from coldguard.data import generate_synthetic_data, validate_sensor_frame
from coldguard.model import ColdGuardModel
from coldguard.storage import add_alert, get_alerts, update_alert, clear_alerts

st.set_page_config(page_title="ColdGuard AI", page_icon="❄️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f4f8fc; }
h1,h2,h3 { font-family: 'Manrope', sans-serif; color: #10243a; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#10243a 0%,#173b59 100%); }
[data-testid="stSidebar"] * { color: #edf7ff !important; }
.hero { background: linear-gradient(120deg,#10243a 0%,#174a70 65%,#2684b9 100%); padding: 1.5rem 1.8rem; border-radius: 18px; color: white; margin-bottom: 1rem; }
.hero h1 { color:white; margin:0; font-size:2.1rem; }
.hero p { color:#d5ebfa; margin:.4rem 0 0 0; }
.kpi { background:white; border:1px solid #e0eaf2; border-radius:16px; padding:17px 18px; box-shadow:0 5px 18px rgba(24,61,91,.05); min-height:120px; }
.kpi-label { font-size:.82rem; color:#60758a; font-weight:600; }
.kpi-value { font-family:'Manrope',sans-serif; font-size:1.8rem; font-weight:800; color:#10243a; margin-top:5px; }
.kpi-foot { font-size:.78rem; color:#668094; margin-top:4px; }
.section-card { background:white; border:1px solid #e0eaf2; border-radius:16px; padding:18px; }
.pill { display:inline-block; padding:4px 10px; border-radius:999px; font-weight:700; font-size:.75rem; background:#e7f4ff; color:#1769aa; }
.small-note { color:#60758a; font-size:.85rem; }
div.stButton > button { border-radius:10px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

if "model" not in st.session_state:
    m = ColdGuardModel()
    m.train()
    st.session_state.model = m
if "demo_temp" not in st.session_state: st.session_state.demo_temp = 4.2
if "demo_humidity" not in st.session_state: st.session_state.demo_humidity = 66
if "door_open" not in st.session_state: st.session_state.door_open = False
if "compressor_on" not in st.session_state: st.session_state.compressor_on = True
if "rising" not in st.session_state: st.session_state.rising = False
if "demo_history" not in st.session_state:
    hist = generate_synthetic_data(rows=180, seed=7)
    st.session_state.demo_history = hist.tail(60).copy()
if "settings" not in st.session_state:
    st.session_state.settings = {"low": 0.25, "high": 0.60, "min_temp": 2.0, "max_temp": 8.0, "window": 30}
if "upload_df" not in st.session_state: st.session_state.upload_df = None

settings = st.session_state.settings
page = st.sidebar.radio("NAVIGATION", ["Overview", "Predictive Analytics", "Alerts Centre", "Sensor Monitoring", "Reports", "Settings"], label_visibility="visible")
st.sidebar.markdown("---")
st.sidebar.markdown("**DEMO ENVIRONMENT**")
st.sidebar.markdown('<span class="pill">Synthetic data mode</span>', unsafe_allow_html=True)
st.sidebar.caption("Prototype only · Not for operational safety decisions")

def current_row():
    h = st.session_state.demo_history
    recent = h["temperature"].tail(6)
    rate = float((recent.iloc[-1] - recent.iloc[0]) / max(len(recent)-1, 1))
    return {
        "temperature": float(st.session_state.demo_temp),
        "humidity": float(st.session_state.demo_humidity),
        "door_open": int(st.session_state.door_open),
        "compressor_on": int(st.session_state.compressor_on),
        "ambient_temperature": 27.0,
        "minutes_since_maintenance": 160.0,
        "temp_rate_5m": rate if not st.session_state.rising else max(rate, 0.12)
    }

row = current_row()
model = st.session_state.model
prob = model.predict_probability(row)
current_excursion = row["temperature"] < settings["min_temp"] or row["temperature"] > settings["max_temp"]
baseline_reasons = []
if row["temp_rate_5m"] > 0.08: baseline_reasons.append("temperature is rising quickly")
if row["door_open"]: baseline_reasons.append("door is open")
if not row["compressor_on"]: baseline_reasons.append("compressor is off")
if row["temperature"] > settings["max_temp"] - 1: baseline_reasons.append("temperature is close to the upper limit")
if current_excursion: baseline_reasons.insert(0, "current temperature is outside configured limits")
if current_excursion: risk = "Current excursion"
elif prob >= settings["high"]: risk = "High"
elif prob >= settings["low"]: risk = "Medium"
else: risk = "Low"

def kpi(label, value, foot, icon):
    st.markdown(f'<div class="kpi"><div class="kpi-label">{icon} &nbsp; {label}</div><div class="kpi-value">{value}</div><div class="kpi-foot">{foot}</div></div>', unsafe_allow_html=True)

def hero(title, subtitle):
    st.markdown(f'<div class="hero"><h1>❄️ {title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

if page == "Overview":
    hero("ColdGuard AI", "Predictive cold-chain monitoring · See risk before a threshold alarm")
    st.caption("DEMO MODE — All sensor readings and predictions are simulated. Configure product-specific limits before any real-world use.")
    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("Current temperature", f'{row["temperature"]:.1f} °C', f'Configured range {settings["min_temp"]:.1f}–{settings["max_temp"]:.1f} °C', "🌡️")
    with c2: kpi("Predicted risk", f'{prob*100:.0f}%', f'{risk} · next {settings["window"]} minutes', "◈")
    with c3: kpi("Humidity", f'{row["humidity"]:.0f}%', "Simulated relative humidity", "💧")
    with c4: kpi("Equipment", "Nominal" if row["compressor_on"] else "Check compressor", "Door " + ("open" if row["door_open"] else "closed"), "⚙️")
    st.write("")
    left,right = st.columns([1.65,1])
    with left:
        st.markdown("### Temperature timeline")
        hist = st.session_state.demo_history.copy()
        hist = pd.concat([hist, pd.DataFrame([{"timestamp":pd.Timestamp.now(),"temperature":row["temperature"]}])], ignore_index=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist["timestamp"], y=hist["temperature"], mode="lines", name="Temperature", line=dict(color="#1685bd", width=3), fill="tozeroy", fillcolor="rgba(22,133,189,.08)"))
        fig.add_hline(y=settings["max_temp"], line_dash="dash", line_color="#e35d6a", annotation_text="Upper limit")
        fig.add_hline(y=settings["min_temp"], line_dash="dash", line_color="#d8a03d", annotation_text="Lower limit")
        fig.update_layout(height=330, margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor="white", plot_bgcolor="white", yaxis_title="°C", xaxis_title="", legend=dict(orientation="h",y=1.1))
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("### Risk assessment")
        color = "#d94f5c" if current_excursion or risk=="High" else "#d89b28" if risk=="Medium" else "#219b7a"
        st.markdown(f'<div class="section-card"><div style="font-size:.8rem;color:#60758a">PREDICTED EXCURSION PROBABILITY</div><div style="font-size:2.8rem;font-weight:800;color:{color}">{prob*100:.1f}%</div><div style="font-weight:700;color:{color}">{risk}</div><hr/><div style="color:#40566a;font-size:.9rem">Prediction target: temperature exceeds configured upper limit within the next {settings["window"]} minutes.</div></div>', unsafe_allow_html=True)
        if baseline_reasons:
            st.markdown("**Why this needs attention**")
            for reason in baseline_reasons: st.write("• " + reason.capitalize())
        else:
            st.success("No baseline rule is currently triggered.")
    st.markdown("### Live demo controls")
    a,b,c,d = st.columns(4)
    with a: st.session_state.demo_temp = st.slider("Temperature (°C)", -2.0, 14.0, float(st.session_state.demo_temp), 0.1)
    with b: st.session_state.demo_humidity = st.slider("Humidity (%)", 20, 100, int(st.session_state.demo_humidity))
    with c: st.session_state.door_open = st.toggle("Door open", value=st.session_state.door_open)
    with d: st.session_state.compressor_on = st.toggle("Compressor on", value=st.session_state.compressor_on)
    x,y,z = st.columns([1,1,2])
    with x:
        if st.button("📈 Simulate rising trend", use_container_width=True):
            st.session_state.rising = True
            st.session_state.demo_temp = min(14.0, st.session_state.demo_temp + 1.2)
            st.session_state.demo_history = pd.concat([st.session_state.demo_history, pd.DataFrame([{"timestamp":pd.Timestamp.now(),"temperature":st.session_state.demo_temp,"humidity":st.session_state.demo_humidity,"door_open":int(st.session_state.door_open),"compressor_on":int(st.session_state.compressor_on),"ambient_temperature":27.0,"minutes_since_maintenance":160,"temp_rate_5m":0.15}])], ignore_index=True).tail(100)
            st.rerun()
    with y:
        if st.button("🚨 Trigger excursion", use_container_width=True):
            st.session_state.demo_temp = settings["max_temp"] + 1.5
            st.session_state.rising = True
            add_alert("High", "Current temperature excursion", f"Simulated temperature {st.session_state.demo_temp:.1f}°C is above configured upper limit {settings['max_temp']:.1f}°C.")
            st.rerun()
    with z:
        if st.button("↻ Reset demo", use_container_width=True):
            st.session_state.demo_temp = 4.2
            st.session_state.demo_humidity = 66
            st.session_state.door_open = False
            st.session_state.compressor_on = True
            st.session_state.rising = False
            st.session_state.demo_history = generate_synthetic_data(rows=180, seed=7).tail(60).copy()
            st.rerun()
    st.markdown('<p class="small-note">The model output is a demonstration using synthetic training data. It is not a calibrated probability for a real facility.</p>', unsafe_allow_html=True)

elif page == "Predictive Analytics":
    hero("Predictive Analytics", "Understand trends, drivers and model behaviour")
    left,right = st.columns([1.4,1])
    with left:
        hist = st.session_state.demo_history
        fig = px.line(hist, x="timestamp", y="temperature", title="Recent temperature history", color_discrete_sequence=["#1685bd"])
        fig.add_hline(y=settings["max_temp"], line_dash="dash", line_color="#e35d6a", annotation_text="Upper limit")
        fig.add_hline(y=settings["min_temp"], line_dash="dash", line_color="#d8a03d", annotation_text="Lower limit")
        fig.update_layout(height=360, paper_bgcolor="white", plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("### Prediction summary")
        st.metric("Excursion probability", f"{prob*100:.1f}%")
        st.metric("Prediction horizon", f'{settings["window"]} minutes')
        st.metric("Current state", "Outside limits" if current_excursion else "Within limits")
        st.info("The future label is defined as any temperature above the configured upper limit in the next prediction window. This starter model trains against an 8°C label; adjust the training label and retrain for other limits.")
    st.markdown("### Feature importance")
    fi = model.feature_importance()
    fi["Readable feature"] = fi["feature"].map({
        "temperature":"Current temperature","humidity":"Humidity","door_open":"Door open",
        "compressor_on":"Compressor status","ambient_temperature":"Ambient temperature",
        "minutes_since_maintenance":"Time since maintenance","temp_rate_5m":"Temperature rate of change"
    })
    f = px.bar(fi, x="importance", y="Readable feature", orientation="h", color="importance", color_continuous_scale=["#ccecff","#147db5"])
    f.update_layout(height=330, showlegend=False, coloraxis_showscale=False, paper_bgcolor="white", plot_bgcolor="white", xaxis_title="Relative model importance", yaxis_title="")
    st.plotly_chart(f, use_container_width=True)
    st.markdown("### Transparent baseline checks")
    if baseline_reasons:
        for reason in baseline_reasons: st.warning(reason.capitalize())
    else:
        st.success("No simple baseline warning triggered by the current demo inputs.")
    st.caption("Feature importance describes model behaviour globally; it is not a causal explanation for an individual prediction.")

elif page == "Alerts Centre":
    hero("Alerts Centre", "Review, acknowledge and resolve generated events")
    if st.button("＋ Log current risk assessment"):
        level = "High" if current_excursion or prob >= settings["high"] else "Medium" if prob >= settings["low"] else "Low"
        detail = f"Risk probability {prob:.1%}; temperature {row['temperature']:.1f}°C; door {'open' if row['door_open'] else 'closed'}; compressor {'on' if row['compressor_on'] else 'off'}. " + ("Baseline: " + ", ".join(baseline_reasons) if baseline_reasons else "No baseline rule triggered.")
        add_alert(level, "Risk assessment recorded", detail)
        st.success("Risk assessment added to persistent alert history.")
    alerts = get_alerts()
    if alerts.empty:
        st.info("No alerts recorded yet. Use the button above or trigger an excursion from Overview.")
    else:
        f1,f2 = st.columns(2)
        with f1: level_filter = st.multiselect("Risk level", ["High","Medium","Low"], default=["High","Medium","Low"])
        with f2: status_filter = st.multiselect("Status", ["Active","Acknowledged","Resolved"], default=["Active","Acknowledged","Resolved"])
        shown = alerts[alerts["level"].isin(level_filter) & alerts["status"].isin(status_filter)]
        st.dataframe(shown, use_container_width=True, hide_index=True)
        st.markdown("### Update an alert")
        ids = shown["id"].astype(int).tolist()
        if ids:
            chosen = st.selectbox("Alert ID", ids)
            action = st.text_input("Operator note", placeholder="e.g., Checked door seal; monitoring temperature")
            p,q = st.columns(2)
            with p:
                if st.button("Acknowledge selected"):
                    update_alert(chosen, "Acknowledged", action); st.rerun()
            with q:
                if st.button("Resolve selected"):
                    update_alert(chosen, "Resolved", action); st.rerun()

elif page == "Sensor Monitoring":
    hero("Sensor Monitoring", "Check sensor quality or load historical CSV data")
    st.markdown("### Simulated sensor status")
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("Temperature sensor", "Online", f'{row["temperature"]:.1f} °C')
    with c2: st.metric("Humidity sensor", "Online", f'{row["humidity"]:.0f}%')
    with c3: st.metric("Door / compressor", "Review" if row["door_open"] or not row["compressor_on"] else "Nominal")
    st.markdown("### Upload historical CSV")
    st.write("Required columns: `timestamp`, `temperature`, `humidity`. Optional: `door_open`, `compressor_on`, `ambient_temperature`, `minutes_since_maintenance`.")
    uploaded = st.file_uploader("Choose sensor CSV", type=["csv"])
    if uploaded is not None:
        try:
            raw = pd.read_csv(uploaded)
            cleaned, warnings = validate_sensor_frame(raw)
            st.session_state.upload_df = cleaned
            st.success(f"Loaded and validated {len(cleaned)} row(s).")
            for warning in warnings: st.warning(warning)
            st.dataframe(cleaned.tail(20), use_container_width=True)
            chart = px.line(cleaned, x="timestamp", y="temperature", title="Uploaded temperature history", color_discrete_sequence=["#1685bd"])
            st.plotly_chart(chart, use_container_width=True)
            st.download_button("Download cleaned CSV", cleaned.to_csv(index=False).encode("utf-8"), "coldguard_cleaned_sensor_data.csv", "text/csv")
        except Exception as e:
            st.error(f"Could not read this CSV: {e}")
    elif st.session_state.upload_df is not None:
        st.caption("Previously uploaded data is available for this session.")
        st.dataframe(st.session_state.upload_df.tail(10), use_container_width=True)
    st.markdown("### Data-quality notes")
    st.write("• Missing required values are removed and reported. • Abrupt jumps greater than 3°C between readings are flagged for review. • Drift detection in this prototype is heuristic, not a calibrated sensor-diagnostics model.")

elif page == "Reports":
    hero("Reports & Evidence", "Export demo readings and review model evaluation")
    df = st.session_state.demo_history.copy()
    df["demo_mode"] = True
    df["configured_min_temp"] = settings["min_temp"]
    df["configured_max_temp"] = settings["max_temp"]
    df["current_excursion"] = (df["temperature"] < settings["min_temp"]) | (df["temperature"] > settings["max_temp"])
    st.markdown("### Summary")
    a,b,c = st.columns(3)
    with a: st.metric("Readings in trend", len(df))
    with b: st.metric("Min / max temperature", f'{df.temperature.min():.1f} / {df.temperature.max():.1f}°C')
    with c: st.metric("Outside configured limits", int(df["current_excursion"].sum()))
    st.download_button("⬇ Download sensor report CSV", df.to_csv(index=False).encode("utf-8"), "coldguard_demo_sensor_report.csv", "text/csv", use_container_width=True)
    alerts = get_alerts()
    if not alerts.empty:
        st.download_button("⬇ Download alert history CSV", alerts.to_csv(index=False).encode("utf-8"), "coldguard_alert_history.csv", "text/csv", use_container_width=True)
    else:
        st.info("Alert history is empty. Create an event in Alerts Centre to enable an alert-history report.")
    st.markdown("### Synthetic holdout evaluation")
    metrics = model.metrics
    x1,x2,x3,x4 = st.columns(4)
    with x1: st.metric("Precision", f'{metrics.get("precision",0):.2f}')
    with x2: st.metric("Recall", f'{metrics.get("recall",0):.2f}')
    with x3: st.metric("F1 score", f'{metrics.get("f1",0):.2f}')
    with x4: st.metric("False-alarm rate", f'{metrics.get("false_alarm_rate",0):.2f}')
    st.warning(metrics.get("note", "Synthetic data only."))
    st.caption("Metrics are calculated from a chronological holdout of synthetic records. A realistic evaluation needs independently collected, labelled facility data.")

elif page == "Settings":
    hero("Settings", "Configure demo thresholds and prediction horizon")
    st.info("These settings affect dashboard alerts and current-excursion checks. The starter ML model's training labels use an 8°C upper threshold; changing settings does not automatically retrain the model.")
    with st.form("settings_form"):
        lower = st.number_input("Lower temperature limit (°C)", value=float(settings["min_temp"]), min_value=-40.0, max_value=20.0, step=0.5)
        upper = st.number_input("Upper temperature limit (°C)", value=float(settings["max_temp"]), min_value=-20.0, max_value=50.0, step=0.5)
        low = st.slider("Medium-risk threshold", 0.05, 0.80, float(settings["low"]), 0.05)
        high = st.slider("High-risk threshold", 0.10, 0.95, float(settings["high"]), 0.05)
        window = st.select_slider("Prediction window", options=[10,15,30,45,60], value=int(settings["window"]))
        submitted = st.form_submit_button("Save settings")
        if submitted:
            if lower >= upper:
                st.error("Lower limit must be less than upper limit.")
            elif low >= high:
                st.error("High-risk threshold must be greater than medium-risk threshold.")
            else:
                st.session_state.settings = {"min_temp":lower,"max_temp":upper,"low":low,"high":high,"window":window}
                st.success("Settings saved for this session.")
                st.rerun()
    st.markdown("### Demo controls")
    st.write("Data source: synthetic sensor simulator and optional user-uploaded CSV.")
    st.write("Storage: local SQLite database for alert history.")
    st.write("Model: Random Forest classifier trained at app startup on generated synthetic data.")
    if st.button("Clear all alert history", type="secondary"):
        clear_alerts()
        st.success("Alert history cleared.")

st.sidebar.markdown("---")
st.sidebar.caption("ColdGuard AI · Student prototype")
