import streamlit as st
from app_blocker import run_blocking, unblock_resources
from device_utils import get_local_ip, get_adb_devices
from ui_utils import setup_page, create_custom_css
import asyncio
import time
from datetime import datetime, timedelta
import pandas as pd

setup_page()
create_custom_css()

st.markdown('<p class="big-font">Advanced App Blocker</p>', unsafe_allow_html=True)

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
    "Netflix": "com.netflix.mediaclient",
    "www.google.com": "http://www.google.com",
    "www.youtube.com": "http://www.youtube.com",
    "www.chat.openai.com": "http://www.chat.openai.com",
    "www.geeksforgeeks.org": "http://www.geeksforgeeks.org"
}


st.sidebar.markdown('<p class="medium-font">Device Management</p>', unsafe_allow_html=True)

local_ip = get_local_ip()
st.sidebar.write(f"Local IP: {local_ip}")

if st.sidebar.button("Scan for Devices", key="scan_devices"):
    with st.spinner("Scanning for devices..."):
        devices = asyncio.run(get_adb_devices())
        st.session_state['devices'] = devices
    if devices:
        st.sidebar.success(f"Found {len(devices)} device(s)")
    else:
        st.sidebar.error("No devices found. Make sure ADB is set up correctly and devices are connected.")

if 'devices' in st.session_state and st.session_state['devices']:
    selected_devices = st.sidebar.multiselect(
        "Select devices to manage",
        options=st.session_state['devices']
    )
else:
    selected_devices = []

col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="medium-font">App Selection</p>', unsafe_allow_html=True)
    
    selected_apps = st.multiselect(
        "Select apps and websites to block",
        options=list(apps_and_websites.keys())
    )

    apps_to_block = [apps_and_websites[app] for app in selected_apps]

    if apps_to_block:
        st.write("Package names to block:", ", ".join(apps_to_block))
    else:
        st.info("No apps selected for blocking.")

with col2:
    st.markdown('<p class="medium-font">Blocking Schedule</p>', unsafe_allow_html=True)

    blocking_type = st.radio("Blocking Type", ["Schedule", "Duration"])

    if blocking_type == "Schedule":
        start_time_str = st.text_input("Start BLocking at (HH\:MM)", value=datetime.now().strftime("%H:%M"))
        end_time_str = st.text_input("End Blocking at (HH\:MM)", value=(datetime.now() + timedelta(hours=1)).strftime("%H:%M"))

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

start_button = st.button("Start Blocking", key="start_button")

stop_button = st.button("Stop Blocking", key="stop_button")

info_placeholder = st.empty()

report_placeholder = st.empty()

is_blocking = False

def update_report():
    report_placeholder.empty()

    if 'blocking_history' not in st.session_state:
        st.session_state['blocking_history'] = []

    st.session_state['blocking_history'].append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Blocked Apps": ", ".join(apps_to_block),
        "Devices": ", ".join(selected_devices)
    })

    report_df = pd.DataFrame(st.session_state['blocking_history'])
    with report_placeholder:
        st.markdown('<p class="medium-font">Blocking Report</p>', unsafe_allow_html=True)
        st.table(report_df)

def is_blocking_time():
    now = datetime.now().time()
    if start_time <= end_time:
        return start_time <= now <= end_time
    else:  
        return now >= start_time or now <= end_time

def blocking_loop():
    if 'blocking_history' not in st.session_state:
        st.session_state['blocking_history'] = []
    if apps_to_block and selected_devices and start_time and end_time:
        is_blocking = True
        st.success("Blocking started!")
        run_blocking(apps_to_block, selected_devices) 
        while is_blocking:
            if st.session_state.get('stop_blocking', False):
                is_blocking = False
                info_placeholder.text("Blocking stopped.")
                unblock_resources(apps_to_block, selected_devices)  
                break

            try:
                if is_blocking_time():
                    blocking_info = run_blocking(apps_to_block, selected_devices)
                    info_placeholder.text(blocking_info)
                    
                    update_report()
                else:
                    unblock_resources(apps_to_block, selected_devices)  
                    info_placeholder.text("Outside of scheduled blocking time.")
                    is_blocking = False
                    break
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                is_blocking = False
                break

            time.sleep(5)  #
    else:
        st.warning("Please select at least one app, one device, and enter valid times before starting.")

if start_button:
    blocking_loop()

if stop_button:
    st.session_state['stop_blocking'] = True

if st.session_state.get('stop_blocking', False):
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
    else:
        st.warning("No blocking history to download.")