import streamlit as st
from app_blocker import run_blocking, get_local_ip, get_adb_devices, get_installed_apps, get_app_usage_stats
import asyncio
import time
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Advanced App Blocker", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
.big-font {
    font-size:30px !important;
    font-weight: bold;
}
.medium-font {
    font-size:20px !important;
    font-weight: bold;
}
.small-font {
    font-size:14px !important;
}
.success {
    color: green;
}
.error {
    color: red;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">Advanced App Blocker</p>', unsafe_allow_html=True)

# Predefined apps and websites (unchanged)
apps_and_websites = {
    "WhatsApp": "com.whatsapp",
    "YouTube": "com.google.android.youtube",
    "Chrome": "com.android.chrome",
    "Twitter": "com.twitter.android",
    "Gallery": "com.android.gallery3d",
    "Camera": "com.android.camera",
    "Files": "com.android.documentsui",
    "LinkedIn": "com.linkedin.android"
}

# Sidebar for device selection and scanning
st.sidebar.markdown('<p class="medium-font">Device Management</p>', unsafe_allow_html=True)

# Get local IP
local_ip = get_local_ip()
st.sidebar.write(f"Local IP: {local_ip}")

# Scan for devices
if st.sidebar.button("Scan for Devices"):
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
    start_time = st.time_input("Start blocking at", value=datetime.now().time())
    end_time = st.time_input("End blocking at", value=(datetime.now() + timedelta(hours=1)).time())
    
    # Create a button to start blocking
    start_button = st.button("Start Blocking")

    # Create a button to stop blocking
    stop_button = st.button("Stop Blocking")

# Create a placeholder for the blocking info
info_placeholder = st.empty()

# Flag to control the blocking loop
is_blocking = False

if start_button:
    if apps_to_block and selected_devices:
        is_blocking = True
        st.success("Blocking started!")
    else:
        st.warning("Please select at least one app and one device before starting.")

if stop_button:
    is_blocking = False
    info_placeholder.text("Blocking stopped.")

# Function to check if current time is within blocking schedule
def is_blocking_time():
    now = datetime.now().time()
    if start_time <= end_time:
        return start_time <= now <= end_time
    else:  # Handles overnight schedules
        return now >= start_time or now <= end_time

# Blocking loop
while is_blocking:
    try:
        if is_blocking_time():
            # Start blocking on selected devices
            blocking_info = run_blocking(apps_to_block, selected_devices)
            info_placeholder.text(blocking_info)
        else:
            info_placeholder.text("Outside of scheduled blocking time.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        is_blocking = False
    
    time.sleep(5)  # Add a delay to prevent excessive scanning

    # Check if the stop button has been pressed
    if stop_button:
        is_blocking = False
        info_placeholder.text("Blocking stopped.")
        break

# Display installed apps and usage statistics
if selected_devices:
    st.markdown('<p class="medium-font">Installed Apps and Usage Statistics</p>', unsafe_allow_html=True)
    for device in selected_devices:
        st.markdown(f'<p class="small-font">Device: {device}</p>', unsafe_allow_html=True)
        
        # Retrieve installed apps
        installed_apps = asyncio.run(get_installed_apps(device))
        
        # Retrieve app usage stats
        usage_stats = asyncio.run(get_app_usage_stats(device))
        
        # Combine and display data
        if installed_apps and usage_stats:
            df = pd.DataFrame({
                'App': installed_apps,
                'Usage Time (minutes)': [usage_stats.get(app, 0) / 60000 for app in installed_apps]  # Convert ms to minutes
            })
            df = df.sort_values('Usage Time (minutes)', ascending=False).head(10)  # Top 10 apps
            
            fig = px.bar(df, x='App', y='Usage Time (minutes)', title=f'Top 10 Apps by Usage Time - {device}')
            st.plotly_chart(fig)
        else:
            st.warning(f"Unable to retrieve data for device {device}")

# Generate and display report
if 'blocking_history' in st.session_state:
    st.markdown('<p class="medium-font">Blocking Report</p>', unsafe_allow_html=True)
    report_df = pd.DataFrame(st.session_state['blocking_history'])
    st.dataframe(report_df)
    
    # Download report as CSV
    csv = report_df.to_csv(index=False)
    st.download_button(
        label="Download Blocking Report",
        data=csv,
        file_name="app_blocking_report.csv",
        mime="text/csv",
    )
