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

# Comprehensive PwC Brand Identity CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap');
    
    /* Global App Styling */
    .stApp {
        background: linear-gradient(135deg, #F1F1F1 0%, #E8E8E8 100%);
        font-family: 'Open Sans', sans-serif;
    }
    
    /* Main Content Area */
    .main .block-container {
        padding: 2rem 1rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 1rem auto;
        backdrop-filter: blur(10px);
    }
    
    /* Headers and Titles */
    .main-header {
        color: #E03C31;
        text-align: center;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        font-family: 'Open Sans', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #E03C31 !important;
        font-family: 'Open Sans', sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Login Container */
    .login-container {
        max-width: 450px;
        margin: 2rem auto;
        padding: 3rem 2.5rem;
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(224, 60, 49, 0.15);
        border: 1px solid rgba(224, 60, 49, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .login-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #E03C31, #FFB612);
    }
    
    /* Buttons - Primary */
    .stButton > button {
        background: linear-gradient(135deg, #E03C31 0%, #c72e24 100%);
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(224, 60, 49, 0.3) !important;
        font-family: 'Open Sans', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #FFB612 0%, #e5a50a 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(255, 182, 18, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Form Elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 2px solid #E8E8E8 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        font-family: 'Open Sans', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #E03C31 !important;
        box-shadow: 0 0 0 3px rgba(224, 60, 49, 0.1) !important;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #E03C31 0%, #c72e24 100%) !important;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #E03C31 0%, #c72e24 100%);
        padding: 1rem;
    }
    
    .sidebar .sidebar-content .element-container {
        color: white !important;
    }
    
    /* Navigation Buttons in Sidebar */
    .stButton[data-testid="baseButton-secondary"] > button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        margin: 0.25rem 0 !important;
    }
    
    .stButton[data-testid="baseButton-secondary"] > button:hover {
        background: rgba(255, 182, 18, 0.9) !important;
        border-color: #FFB612 !important;
    }
    
    .stButton[data-testid="baseButton-primary"] > button {
        background: #FFB612 !important;
        color: #333333 !important;
        border: none !important;
        font-weight: 700 !important;
    }
    
    /* Tables */
    .stDataFrame {
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(90deg, #d4edda, #c3e6cb) !important;
        border: none !important;
        border-radius: 10px !important;
        border-left: 4px solid #28a745 !important;
    }
    
    .stError {
        background: linear-gradient(90deg, #f8d7da, #f1aeb5) !important;
        border: none !important;
        border-radius: 10px !important;
        border-left: 4px solid #dc3545 !important;
    }
    
    .stInfo {
        background: linear-gradient(90deg, #cce7ff, #b3d9ff) !important;
        border: none !important;
        border-radius: 10px !important;
        border-left: 4px solid #E03C31 !important;
    }
    
    /* File Uploader */
    .stFileUploader {
        border: 2px dashed #E03C31 !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        background: rgba(224, 60, 49, 0.05) !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader:hover {
        border-color: #FFB612 !important;
        background: rgba(255, 182, 18, 0.05) !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #E03C31, #c72e24) !important;
        color: white !important;
        border-radius: 10px 10px 0 0 !important;
        font-weight: 600 !important;
    }
    
    /* Progress Bars */
    .stProgress .st-bo {
        background-color: #E03C31 !important;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #E03C31;
        margin: 1rem 0;
    }
    
    /* Accent Elements */
    .accent-text {
        color: #FFB612 !important;
        font-weight: 600 !important;
    }
    
    .pwc-divider {
        height: 3px;
        background: linear-gradient(90deg, #E03C31, #FFB612);
        border: none;
        border-radius: 2px;
        margin: 2rem 0;
    }
    
    /* Background Pattern */
    body {
        background-image: 
            radial-gradient(circle at 25% 25%, rgba(224, 60, 49, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 75% 75%, rgba(255, 182, 18, 0.05) 0%, transparent 50%);
    }
    
    /* Download Buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(40, 167, 69, 0.3) !important;
    }
    
    /* Charts and Visualizations */
    .stPlotlyChart, .stPyplotGlobalUse {
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        overflow: hidden !important;
    }
    
    /* Custom Animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
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
    
    if 'reviewer_notes' not in st.session_state:
        st.session_state.reviewer_notes = {}
    
    if 'edited_report_content' not in st.session_state:
        st.session_state.edited_report_content = None
    
    if 'final_reviewer_notes' not in st.session_state:
        st.session_state.final_reviewer_notes = ""

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
