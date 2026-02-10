import time
import streamlit as st
from data_loader import fetch_telemetry

# --- Page Config ---
st.set_page_config(
    page_title="Agri-Stack Dashboard",
    page_icon="🐔",
    layout="wide"
)

# --- Header ---
st.title("🐔 Agri-Stack: Brooder Monitor")
st.markdown("Real-time telemetry from **ESP32 Mock Sensors**.")
@st.fragment(run_every=3)
def render_dashboard():
    # Show Last Updated time - this needs to be INSIDE the fragment to update!
    st.caption(f"Last Updated: {time.strftime('%H:%M:%S')}")

    # --- Fetch Data ---
    df = fetch_telemetry(limit=50)

    if df.empty:
        st.warning("No data found. Waiting for sensor...")
        return

    # Get Latest Values
    latest = df.iloc[-1]

    # --- KPI Metrics Row ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Temperature (°C)",
            value=f"{latest['temperature']:.1f}",
            delta=f"{latest['temperature'] - 30.0:.1f}",
            delta_color="inverse"
        )

    with col2:
        st.metric(
            label="Humidity (%)",
            value=f"{latest['humidity']:.1f}",
            delta="Normal" if 50 <= latest['humidity'] <= 70 else "Alert"
        )
        
    with col3:
        st.metric(
            label="Ammonia (ppm)",
            value=f"{latest['ammonia_ppm']:.2f}",
            delta_color="inverse",
            delta="High" if latest['ammonia_ppm'] > 20 else "Safe"
        )

    # --- Charts ---
    st.divider()

    col_charts_1, col_charts_2 = st.columns(2)

    with col_charts_1:
        st.subheader("Temperature Trend")
        st.line_chart(
            df.set_index("timestamp")[["temperature"]], 
            color="#FF4B4B",
            height=300
        )

    with col_charts_2:
        st.subheader("Humidity Trend")
        st.line_chart(
            df.set_index("timestamp")[["humidity"]], 
            color="#0068C9",
            height=300
        )

    # --- Alerts ---
    if latest['temperature'] > 35.0:
        st.error(f"🔥 HIGH TEMP ALERT: {latest['temperature']}°C")

    if latest['ammonia_ppm'] > 1.0:
        st.warning(f"⚠️ High Ammonia Detected: {latest['ammonia_ppm']} ppm")

    # --- Raw Data View ---
    with st.expander("📊 View Raw Data (Last 50 records)", expanded=False):
        st.dataframe(
            df[["timestamp", "temperature", "humidity", "ammonia_ppm", "device_id"]],
            hide_index=True,
            use_container_width=True,
            width='stretch' # Keeping this for now as width='stretch' might be version specific?
            # actually the warning is very specific. But 'width' param in st.dataframe is usually int.
            # Let's try removing it first, as default is usually full width in expander.
        )

# Run the dashboard fragment
render_dashboard()
