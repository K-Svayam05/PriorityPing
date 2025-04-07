import streamlit as st
import requests
import time

st.title("PriorityPing Dashboard")

# --- Configuration ---
# IMPORTANT: UPDATE THIS API_ENDPOINT to your DEPLOYED BACKEND API URL!
# For example, if your backend is deployed on Vercel at 
# https://priorityping-backend-app.vercel.app, then set:
# API_ENDPOINT = "https://priorityping-backend-app.vercel.app/process_message"

API_ENDPOINT = "https://priority-ping.netlify.app/process_message"  # <-- REPLACE THIS WITH YOUR ACTUAL DEPLOYED API URL

message_container = st.empty() # Container to hold messages

st.subheader("Send Test Message")
test_message = st.text_input("Enter message to test priority:")
if st.button("Check Priority"):
    if test_message:
        try:
            response = requests.post(API_ENDPOINT, json={"text": test_message})
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            st.write(f"Message: '{data['message']}', Priority: **{data['priority']}**")
        except requests.exceptions.RequestException as e:
            st.error(f"Error processing message: {e}")

st.subheader("Recent Messages (Simulated)")
st.write("This section will eventually show real-time messages processed by PriorityPing.")

# --- Simulated Message Display (Replace with real-time data later) ---
messages_data = [
    {"text": "Server down in Prod – need immediate fix!", "priority": "High"},
    {"text": "Friday lunch order is open!", "priority": "Low"},
    {"text": "Team meeting at 2 PM", "priority": "Medium"},
    {"text": "Critical security vulnerability reported!", "priority": "High"},
]

message_display_area = st.container()
with message_display_area:
    for msg in messages_data:
        col1, col2 = st.columns([3, 1]) # Adjust column widths as needed
        with col1:
            st.write(msg['text'])
        with col2:
            st.markdown(f"<span style='background-color: {'red' if msg['priority'] == 'High' else ('orange' if msg['priority'] == 'Medium' else 'lightgreen')}; padding: 5px; border-radius: 5px;'>{msg['priority']} Priority</span>", unsafe_allow_html=True)
        st.divider() # Separator between messages

st.sidebar.header("Panic Button (Placeholder)")
if st.sidebar.button("Escalate Message"):
    st.sidebar.warning("Panic Button functionality not fully implemented in this MVP.")
    # --- (Future: Implement manual escalation logic here) ---

st.sidebar.markdown("---")
st.sidebar.markdown("PriorityPing - 1-Day MVP")