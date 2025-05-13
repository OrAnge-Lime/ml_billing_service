# streamlit_ui/pages/4_Profile.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="User Profile", page_icon="👤")

from api_client import get_prediction_history, get_user_credits

st.title("👤 User Profile & History")

# --- Authentication Check ---
if not st.session_state.get("logged_in"):
    st.warning("Please log in to view your profile.")
    st.stop()

# --- Display User Info ---
user_info = st.session_state.get("user_info", {})
st.subheader(f"Username: {user_info.get('username', 'N/A')}")

# Fetch latest credits
current_credits = get_user_credits()
if current_credits is not None:
    st.session_state.user_info['credits'] = current_credits
    st.metric(label="💰 Current Credits", value=current_credits)
else:
    st.warning("Could not fetch credit balance.")

st.markdown("---")

# --- Add Credits (Placeholder) ---
st.subheader("💸 Add Credits")
col1, col2 = st.columns([1, 1])
with col1:
    add_amount = st.number_input("Amount to add", min_value=1, max_value=1000, value=10, step=1)
with col2:
    st.markdown("<br/>", unsafe_allow_html=True) # Align button vertically
    add_button = st.button("💳 Process Payment")

if add_button:
    # Placeholder - Replace with actual payment integration logic later
    st.info(f"Payment processing for {add_amount} credits is not implemented yet.")
    # Demo: Add locally to session state (will reset on refresh)
    # if isinstance(st.session_state.user_info.get('credits'), int):
    #     st.session_state.user_info['credits'] += add_amount
    #     st.success(f"{add_amount} credits added (UI demo only). Refreshing...")
    #     st.rerun()


st.markdown("---")

# --- Prediction History ---
st.subheader("📜 Transcription History")

limit = st.number_input("Number of records to show:", min_value=5, max_value=200, value=20, step=5)

fetch_history = st.button("🔄 Refresh History")

# Use caching to avoid refetching constantly unless button is pressed
# Or fetch directly on load/button press if data freshness is critical
# Let's fetch on button press or initial load for simplicity here.

@st.cache_data(ttl=60) # Cache data for 60 seconds
def fetch_data(limit_param):
    with st.spinner("Fetching history..."):
        history = get_prediction_history(limit=limit_param)
    return history

# Trigger fetch if button is pressed or if history is not in session state
if fetch_history or "prediction_history" not in st.session_state:
    st.session_state.prediction_history = fetch_data(limit)


history_data = st.session_state.get("prediction_history")

if history_data:
    if not history_data:
        st.info("No prediction history found.")
    else:
        # Prepare data for display
        display_data = []
        for item in history_data:
            # Safely access input_data dictionary keys
            input_meta = item.get("input_data", {})
            if isinstance(input_meta, str): # Handle potential non-dict data if logged incorrectly
                input_meta = {"info": input_meta}

            display_data.append({
                "Timestamp": pd.to_datetime(item.get("timestamp")).strftime('%Y-%m-%d %H:%M:%S') if item.get("timestamp") else "N/A",
                "Model ID": input_meta.get("model_identifier_requested_from_db", "N/A"), # Fetch model name if needed
                "Status": item.get("status", "N/A"),
                "Cost": item.get("cost_charged", "N/A"),
                "Filename": input_meta.get("original_filename", "N/A"),
                "Result/Error": item.get("output_data") if item.get("status") == "success" else item.get("error_message", "N/A")
            })

        df = pd.DataFrame(display_data)

        # Customize dataframe display if needed
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                 "Timestamp": st.column_config.DatetimeColumn("Time", format="YYYY-MM-DD HH:mm:ss"),
                 "Result/Error": st.column_config.TextColumn("Result / Error Details", width="large"),
                 "Cost": st.column_config.NumberColumn("Credits Used", format="%d")
            }
        )

elif history_data is None: # Explicitly check for None if API call failed
     st.error("Failed to load prediction history.")

else: # history_data is an empty list []
     st.info("No prediction history found.")