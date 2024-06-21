import streamlit as st
from Computer import main_app
from Trail import streamlit_app

# Add a navigation sidebar
selected_page = st.sidebar.radio("Select Page", ["Advanced App Blocker", "Network App Blocker"])

# Show the selected page
if selected_page == "Advanced App Blocker":
    streamlit_app.main()
# elif selected_page == "Network App Blocker":
#     main_app.main()
