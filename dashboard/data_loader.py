import os
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Securely load credentials
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

@st.cache_resource
def init_connection():
    """
    Initialize Supabase client. Cached to avoid re-connection on every run.
    """
    if not url or not key:
        st.error("Missing Supabase credentials in .env")
        st.stop()
    return create_client(url, key)

supabase = init_connection()

# Removing cache to force fresh data on every run
# @st.cache_data(ttl=5) 
def fetch_telemetry(limit=50):
    """
    Fetch lateset telemetry data.
    Limit rows to minimize memory usage (Top 50 is enough for real-time trends).
    """
    try:
        response = supabase.table("brooder_telemetry")\
            .select("timestamp, temperature, humidity, ammonia_ppm, device_id")\
            .order("timestamp", desc=True)\
            .limit(limit)\
            .execute()
        
        data = response.data
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by timestamp ascending for the chart (Time goes Left -> Right)
        df = df.sort_values('timestamp')
        
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()
