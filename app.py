import streamlit as st
import os
import sys
from datetime import datetime
import logging
from pathlib import Path

# Import our modules
import login
import psur_app
from utils import setup_logging

# Configure page
st.set_page_config(
    page_title="Pharma Pulse",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for PwC branding
st.markdown("""
<style>
    .main-header {
        color: #E03C31;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button {
        background-color: #E03C31;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #c72e24;
    }
    
    .accent-text {
        color: #FFB612;
        font-weight: bold;
    }
    
    .sidebar .sidebar-content {
        background-color: #F1F1F1;
    }
</style>
""", unsafe_allow_html=True)

def initialize_app():
    """Initialize application state and logging"""
    
    # Create necessary directories
    os.makedirs("output", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Setup logging
    setup_logging()
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'role' not in st.session_state:
        st.session_state.role = None
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = {}
    
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = {}

def main():
    """Main application entry point"""
    
    # Initialize app
    initialize_app()
    
    # Route to appropriate page based on authentication state
    if not st.session_state.authenticated:
        login.show_login_page()
    else:
        # Check if role is stored in session
        if 'role' not in st.session_state or st.session_state.role is None:
            st.error("Unauthorized. Please log in.")
            st.stop()
        else:
            psur_app.main_app()

if __name__ == "__main__":
    main()
