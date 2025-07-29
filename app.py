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

# Clean PwC Brand Identity CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=Open+Sans:wght@300;400;600;700&display=swap');
    
    /* Global Clean App Styling */
    .stApp {
        background: #FFFFFF;
        font-family: 'Montserrat', 'Open Sans', sans-serif;
        min-height: 100vh;
        color: #333333;
    }
    
    /* Login page background with pharmaceutical image */
    .login-page-bg {
        background: url('pharma_background.jpg') center/cover fixed;
        min-height: 100vh;
        position: relative;
    }
    
    .login-page-bg::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(224, 60, 49, 0.1);
        z-index: 0;
    }
    
    /* Main Content Area - Clean White Background */
    .main .block-container {
        padding: 2rem;
        background: #FFFFFF;
        border-radius: 0;
        box-shadow: none;
        margin: 0 auto;
        border: none;
        max-width: 1200px;
    }
    
    /* Clean Headers and Titles */
    .main-header {
        color: #E03C31;
        text-align: center;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 2rem;
        font-family: 'Open Sans', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #E03C31 !important;
        font-family: 'Open Sans', sans-serif !important;
        font-weight: 600 !important;
        background: transparent !important;
    }
    
    /* Fix all header and text color issues */
    .stApp header, .stApp .stMarkdown h1, .stApp .stMarkdown h2, .stApp .stMarkdown h3 {
        background: transparent !important;
        color: #E03C31 !important;
    }
    
    /* Fix sidebar toggle button - make it visible */
    .stApp div[data-testid="stHeader"], .stApp div[data-testid="stToolbar"] {
        background: transparent !important;
    }
    
    /* Sidebar toggle button - PwC orange theme */
    .stApp button[data-testid="collapsedControl"], button[kind="headerNoPadding"] {
        background: #FFB612 !important;
        color: #333333 !important;
        border: 1px solid #e5a50a !important;
        border-radius: 4px !important;
        padding: 0.5rem !important;
        font-weight: 600 !important;
    }
    
    .stApp button[data-testid="collapsedControl"]:hover, button[kind="headerNoPadding"]:hover {
        background: #E03C31 !important;
        color: white !important;
    }
    
    /* Alternative selector for sidebar toggle */
    .css-vk3wp9, .css-1kyxreq {
        background: #FFB612 !important;
        color: #333333 !important;
        border: 1px solid #e5a50a !important;
    }
    
    /* Fix CSV upload text visibility */
    .stApp div, .stApp span, .stApp p {
        background: transparent !important;
    }
    
    /* Ensure file uploader text is visible */
    .stFileUploader label, .stFileUploader .stMarkdown, .stFileUploader div {
        color: #333333 !important;
        background: transparent !important;
    }
    
    .stFileUploader .stMarkdown p, .stFileUploader .stMarkdown span {
        color: #333333 !important;
    }
    
    /* Fix all text elements in main content */
    .main .block-container p, .main .block-container span, .main .block-container div {
        color: #333333 !important;
    }
    
    /* Clean login form styling */
    .stForm {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        border: 2px solid #E03C31 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
        position: relative;
        z-index: 1;
    }
    
    /* Clean input styling */
    .stTextInput > div > div > input, .stTextInput input {
        background: #FFFFFF !important;
        border: 2px solid #E8E8E8 !important;
        color: #333333 !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput > div > div > input:focus, .stTextInput input:focus {
        background: #FFFFFF !important;
        border-color: #E03C31 !important;
        box-shadow: 0 0 0 3px rgba(224, 60, 49, 0.15) !important;
    }
    
    /* Fix password input show/hide button */
    .stTextInput button, .stTextInput > div > div button {
        background: #E03C31 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
    }
    
    .stTextInput button:hover, .stTextInput > div > div button:hover {
        background: #FFB612 !important;
        color: #333333 !important;
    }
    
    /* Clean Buttons - Primary and Form Submit */
    .stButton > button, button[data-testid="baseButton-primary"], .stFormSubmitButton > button {
        background: #E03C31 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        font-family: 'Open Sans', sans-serif !important;
    }
    
    .stButton > button:hover, button[data-testid="baseButton-primary"]:hover, .stFormSubmitButton > button:hover {
        background: #FFB612 !important;
        color: #333333 !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button:active, button[data-testid="baseButton-primary"]:active, .stFormSubmitButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Enhanced Form Elements - Fixed Color Contrast */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 2px solid #E8E8E8 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        font-family: 'Montserrat', 'Open Sans', sans-serif !important;
        transition: all 0.3s ease !important;
        background-color: #FFFFFF !important;
        color: #333333 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #E03C31 !important;
        box-shadow: 0 0 0 3px rgba(224, 60, 49, 0.15) !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #999999 !important;
    }
    
    /* Form Labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label {
        color: #333333 !important;
        font-weight: 600 !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    
    /* Clean Sidebar Styling - Fix Black Background */
    .css-1d391kg, .css-1lcbmhc {
        background: #E03C31 !important;
    }
    
    .stSidebar > div:first-child {
        background: #E03C31 !important;
    }
    
    .sidebar .sidebar-content {
        background: #E03C31 !important;
        padding: 1rem;
    }
    
    .sidebar .sidebar-content .element-container {
        color: white !important;
    }
    
    .sidebar .sidebar-content h1, .sidebar .sidebar-content h2, .sidebar .sidebar-content h3 {
        color: white !important;
    }
    
    /* Fix Pharma Pulse text visibility in sidebar */
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar .stMarkdown h1, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 {
        color: white !important;
        background: transparent !important;
    }
    
    .stSidebar .stMarkdown p, .stSidebar .stMarkdown div, .stSidebar .stMarkdown span {
        color: white !important;
        background: transparent !important;
    }
    
    /* Fix all sidebar elements and backgrounds */
    .stSidebar .stSelectbox label, .stSidebar .stButton label, .stSidebar div[data-testid="stMarkdownContainer"] {
        color: white !important;
    }
    
    /* More comprehensive sidebar fixes */
    .stSidebar, .stSidebar > div, .stSidebar .element-container, .stSidebar .stMarkdown {
        background: #E03C31 !important;
        color: white !important;
    }
    
    .stSidebar button {
        background: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    .stSidebar button:hover {
        background: #FFB612 !important;
        color: #333333 !important;
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
    
    /* Enhanced Tables with PwC Styling */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid rgba(224, 60, 49, 0.1) !important;
    }
    
    .stDataFrame table {
        background: #FFFFFF !important;
    }
    
    .stDataFrame thead tr {
        background: linear-gradient(90deg, #E03C31, #c72e24) !important;
    }
    
    .stDataFrame thead th {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-family: 'Montserrat', sans-serif !important;
        padding: 1rem 0.75rem !important;
        border: none !important;
    }
    
    .stDataFrame tbody tr {
        color: #333333 !important;
    }
    
    .stDataFrame tbody tr:nth-child(even) {
        background-color: rgba(241, 241, 241, 0.5) !important;
    }
    
    .stDataFrame tbody tr:nth-child(odd) {
        background-color: #FFFFFF !important;
    }
    
    .stDataFrame tbody tr:hover {
        background-color: rgba(224, 60, 49, 0.05) !important;
        transition: background-color 0.2s ease !important;
    }
    
    .stDataFrame tbody td {
        padding: 0.75rem !important;
        border: none !important;
        border-bottom: 1px solid rgba(224, 60, 49, 0.1) !important;
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
    
    /* Enhanced Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #E03C31;
        margin: 1rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card h3, .metric-card h4, .metric-card h5 {
        color: #E03C31 !important;
        font-family: 'Montserrat', sans-serif !important;
        margin-bottom: 1rem !important;
    }
    
    .metric-card p, .metric-card li, .metric-card div {
        color: #333333 !important;
        line-height: 1.6 !important;
    }
    
    .metric-card ul {
        margin: 0 !important;
        padding-left: 1.5rem !important;
    }
    
    .metric-card code {
        background: rgba(224, 60, 49, 0.1) !important;
        color: #E03C31 !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
        font-family: 'Monaco', 'Consolas', monospace !important;
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
    
    /* Clean background - no patterns */
    body {
        background: #FFFFFF;
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
    
    /* Enhanced Animations and Responsiveness */
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
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .pulse-hover:hover {
        animation: pulse 0.6s ease-in-out;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .login-container {
            margin: 1rem;
            padding: 2rem 1.5rem;
            max-width: 95%;
        }
        
        .main-header {
            font-size: 2.2rem !important;
        }
        
        .metric-card {
            margin: 0.5rem 0;
            padding: 1rem;
        }
        
        .main .block-container {
            padding: 0.5rem;
            margin: 0.5rem;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            font-size: 1.8rem !important;
        }
        
        .login-container {
            padding: 1.5rem 1rem;
        }
    }
    
    /* Ensure readable text colors */
    .stApp {
        color: #333333;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #E03C31 !important;
    }
    
    .stMarkdown p, .stMarkdown div, .stMarkdown span, .stMarkdown li {
        color: #333333 !important;
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
