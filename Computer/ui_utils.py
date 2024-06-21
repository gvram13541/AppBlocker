import streamlit as st

def setup_page():
    st.set_page_config(page_title="Network App Blocker", layout="wide")

def create_custom_css():
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