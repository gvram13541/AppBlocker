import streamlit as st
from app_blocker import run_blocking, unblock_apps
from device_utils import get_local_ip, get_adb_devices
from ui_utils import setup_page, create_custom_css
import asyncio
import time
from datetime import datetime, timedelta
import pandas as pd

# Setup page and custom CSS
setup_page()
create_custom_css()

st.markdown('<p class="big-font">Advanced App Blocker</p>', unsafe_allow_html=True)

# Predefined apps and websites
apps_and_websites = {
    "WhatsApp": "com.whatsapp",
    "YouTube": "com.google.android.youtube",
    "Chrome": "com.android.chrome",
    "Facebook": "com.facebook.katana",
    "Instagram": "com.instagram.android",
    "Snapchat": "com.snapchat.android",
    "Twitter": "com.twitter.android",
    "TikTok": "com.zhiliaoapp.musically",
    "Spotify": "com.spotify.music",
    "Netflix": "com.netflix.mediaclient"
}


# Sidebar for device selection and scanning
st.sidebar.markdown('<p class="medium-font">Device Management</p>', unsafe_allow_html=True)

# Get local IP
local_ip = get_local_ip()
st.sidebar.write(f"Local IP: {local_ip}")

# Scan for devices
if st.sidebar.button("Scan for Devices", key="scan_devices"):
    with st.spinner("Scanning for devices..."):
        devices = asyncio.run(get_adb_devices())
        st.session_state['devices'] = devices
    if devices:
        st.sidebar.success(f"Found {len(devices)} device(s)")
    else:
        st.sidebar.error("No devices found. Make sure ADB is set up correctly and devices are connected.")

# Select devices
if 'devices' in st.session_state and st.session_state['devices']:
    selected_devices = st.sidebar.multiselect(
        "Select devices to manage",
        options=st.session_state['devices']
    )
else:
    selected_devices = []

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="medium-font">App Selection</p>', unsafe_allow_html=True)
    
    # Create multiselect for apps and websites
    selected_apps = st.multiselect(
        "Select apps and websites to block",
        options=list(apps_and_websites.keys())
    )

    # Convert selected apps to package names
    apps_to_block = [apps_and_websites[app] for app in selected_apps]

    # Display selected package names
    if apps_to_block:
        st.write("Package names to block:", ", ".join(apps_to_block))
    else:
        st.info("No apps selected for blocking.")

with col2:
    st.markdown('<p class="medium-font">Blocking Schedule</p>', unsafe_allow_html=True)

    # Schedule blocking
    blocking_type = st.radio("Blocking Type", ["Schedule", "Duration"])

    if blocking_type == "Schedule":
        start_time_str = st.text_input("Start blocking at (HH:MM)", value=datetime.now().strftime("%H:%M"))
        end_time_str = st.text_input("End blocking at (HH:MM)", value=(datetime.now() + timedelta(hours=1)).strftime("%H:%M"))

        def parse_time(time_str):
            return datetime.strptime(time_str, "%H:%M").time()

        try:
            start_time = parse_time(start_time_str)
            end_time = parse_time(end_time_str)
        except ValueError:
            st.error("Invalid time format. Please enter time in HH:MM format.")
            start_time = end_time = None

    else:
        duration = st.text_input("Enter duration (e.g., 1h30m, 45m, 2h)", value="1h")

        def parse_duration(duration_str):
            hours = 0
            minutes = 0
            if 'h' in duration_str:
                hours, duration_str = duration_str.split('h')
                hours = int(hours)
            if 'm' in duration_str:
                minutes = int(duration_str.replace('m', ''))
            return timedelta(hours=hours, minutes=minutes)

        duration_td = parse_duration(duration)
        start_time = datetime.now().time()
        end_time = (datetime.now() + duration_td).time()

# Create a button to start blocking
start_button = st.button("Start Blocking", key="start_button")

# Create a button to stop blocking
stop_button = st.button("Stop Blocking", key="stop_button")

# Create a placeholder for the blocking info
info_placeholder = st.empty()

# Create a placeholder for the real-time report
report_placeholder = st.empty()

# Flag to control the blocking loop
is_blocking = False

def update_report():
    # Clear the existing report content
    report_placeholder.empty()

    if 'blocking_history' not in st.session_state:
        st.session_state['blocking_history'] = []

    # Simulate app blocking data
    st.session_state['blocking_history'].append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Blocked Apps": ", ".join(apps_to_block),
        "Devices": ", ".join(selected_devices)
    })

    report_df = pd.DataFrame(st.session_state['blocking_history'])
    with report_placeholder:
        st.markdown('<p class="medium-font">Blocking Report</p>', unsafe_allow_html=True)
        st.table(report_df)

# Function to check if current time is within blocking schedule
def is_blocking_time():
    now = datetime.now().time()
    if start_time <= end_time:
        return start_time <= now <= end_time
    else:  # Handles overnight schedules
        return now >= start_time or now <= end_time

if start_button:
    if 'blocking_history' not in st.session_state:
        st.session_state['blocking_history'] = []
    if apps_to_block and selected_devices and start_time and end_time:
        is_blocking = True
        st.success("Blocking started!")
        run_blocking(apps_to_block, selected_devices)  # Block apps immediately
        while is_blocking:
            try:
                if is_blocking_time():
                    blocking_info = run_blocking(apps_to_block, selected_devices)
                    info_placeholder.text(blocking_info)
                    
                    # Update and display the real-time report
                    update_report()
                else:
                    unblock_apps(apps_to_block, selected_devices)  # Unblock apps when outside scheduled time
                    info_placeholder.text("Outside of scheduled blocking time.")
                    is_blocking = False
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                is_blocking = False
            
            # Check if the stop button has been pressed
            if stop_button:  # No key argument here
                is_blocking = False
                info_placeholder.text("Blocking stopped.")
                unblock_apps(apps_to_block, selected_devices)  # Unblock apps when stop button pressed
                
                # Show download button for the final report
                report_df = pd.DataFrame(st.session_state['blocking_history'])
                if not report_df.empty:
                    csv = report_df.to_csv(index=False)
                    st.download_button(
                        label="Download Blocking Report",
                        data=csv,
                        file_name="app_blocking_report.csv",
                        mime="text/csv",
                        key="download_button"
                    )
                break

            time.sleep(5)  # Add a delay to prevent excessive scanning

            # Create a button to stop blocking
        stop_button = st.button("Stop Blocking", key="stop_button_outside")
    else:
        st.warning("Please select at least one app, one device, and enter valid times before starting.")