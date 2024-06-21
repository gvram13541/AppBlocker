import streamlit as st
from network_blocker import run_blocking, unblock_resources
from network_utils import discover_computers
from ui_utils import setup_page, create_custom_css


setup_page()
create_custom_css()

st.markdown('<p class="big-font">Network App Blocker</p>', unsafe_allow_html=True)

st.sidebar.markdown('<p class="medium-font">Network Configuration</p>', unsafe_allow_html=True)
subnet = st.sidebar.text_input("Enter subnet address (e.g., 192.168.1)", value="192.168.1")
username = st.sidebar.text_input("Enter username")
password = st.sidebar.text_input("Enter password", type="password")

st.markdown('<p class="medium-font">App and Website Selection</p>', unsafe_allow_html=True)

resources = st.multiselect(
    "Select apps and websites to block",
    options=["chrome.exe", "firefox.exe", "www.facebook.com", "www.twitter.com"]
)

start_button = st.button("Start Blocking", key="start_button")

stop_button = st.button("Stop Blocking", key="stop_button")

info_placeholder = st.empty()

report_placeholder = st.empty()

if start_button:
    if subnet and username and password and resources:
        computers = discover_computers(subnet)
        if computers:
            result = run_blocking(computers, username, password, resources)
            info_placeholder.success(result)
        else:
            info_placeholder.error("No computers found on the network.")
    else:
        info_placeholder.warning("Please provide subnet, username, password, and select resources.")

if stop_button:
    if subnet and username and password and resources:
        computers = discover_computers(subnet)
        if computers:
            result = unblock_resources(computers, username, password, resources)
            info_placeholder.success(result)
        else:
            info_placeholder.error("No computers found on the network.")
    else:
        info_placeholder.warning("Please provide subnet, username, password, and select resources.")