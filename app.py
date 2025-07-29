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

# Comprehensive PwC Brand Identity CSS with Pharmaceutical Background
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=Open+Sans:wght@300;400;600;700&display=swap');
    
    /* Global App Styling */
    .stApp {
        background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMjAwIDgwMCI+CiAgPGRlZnM+CiAgICA8bGluZWFyR3JhZGllbnQgaWQ9ImJnR3JhZGllbnQiIHgxPSIwJSIgeTE9IjAlIiB4Mj0iMTAwJSIgeTI9IjEwMCUiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAlIiBzdHlsZT0ic3RvcC1jb2xvcjojODdDRUVCO3N0b3Atb3BhY2l0eToxIiAvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0eWxlPSJzdG9wLWNvbG9yOiNCMEUwRTY7c3RvcC1vcGFjaXR5OjEiIC8+CiAgICA8L2xpbmVhckdyYWRpZW50PgogICAgPHBhdHRlcm4gaWQ9ImRvdHMiIHg9IjAiIHk9IjAiIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj4KICAgICAgPGNpcmNsZSBjeD0iNTAiIGN5PSI1MCIgcj0iMiIgZmlsbD0icmdiYSgyNTUsMjU1LDI1NSwwLjMpIi8+CiAgICA8L3BhdHRlcm4+CiAgPC9kZWZzPgogIDxyZWN0IHdpZHRoPSIxMjAwIiBoZWlnaHQ9IjgwMCIgZmlsbD0idXJsKCNiZ0dyYWRpZW50KSIvPgogIDxyZWN0IHdpZHRoPSIxMjAwIiBoZWlnaHQ9IjgwMCIgZmlsbD0idXJsKCNkb3RzKSIvPgogIDxlbGxpcHNlIGN4PSIxNTAiIGN5PSIxMjAiIHJ4PSIyNSIgcnk9IjE1IiBmaWxsPSIjRkY4QzQyIiBvcGFjaXR5PSIwLjgiLz4KICA8ZWxsaXBzZSBjeD0iMjAwIiBjeT0iMTAwIiByeD0iMjUiIHJ5PSIxNSIgZmlsbD0iI0ZGOEMxMiIgb3BhY2l0eT0iMC44Ii8+CiAgPGVsbGlwc2UgY3g9IjEwMCIgY3k9IjE0MCIgcng9IjI1IiByeT0iMTUiIGZpbGw9IiNGRjhDNDIiIG9wYWNpdHk9IjAuOCIvPgogIDxyZWN0IHg9Ijg1MCIgeT0iODAiIHdpZHRoPSIzMCIgaGVpZ2h0PSI2MCIgcng9IjE1IiBmaWxsPSIjNEE5MEUyIiBvcGFjaXR5PSIwLjgiLz4KICA8cmVjdCB4PSI4NTAiIHk9IjgwIiB3aWR0aD0iMzAiIGhlaWdodD0iMzAiIHJ4PSIxNSIgZmlsbD0iI0ZGRkZGRiIgb3BhY2l0eT0iMC45Ii8+CiAgPHJlY3QgeD0iMTAwMCIgeT0iMTUwIiB3aWR0aD0iODAiIGhlaWdodD0iMTIwIiByeD0iMTAiIGZpbGw9IiNEMjY5MUUiIG9wYWNpdHk9IjAuOCIvPgogIDxwYXRoIGQ9Ik01MCA1MDAgUTEwMCA0NTAgMTUwIDUwMCBRMjAwIDU1MCAyNTAgNTAwIiBzdHJva2U9IiMyQzNFNTAiIHN0cm9rZS13aWR0aD0iOCIgZmlsbD0ibm9uZSIgb3BhY2l0eT0iMC43Ii8+CiAgPGNpcmNsZSBjeD0iNTAiIGN5PSI1MDAiIHI9IjIwIiBmaWxsPSIjMkMzRTUwIiBvcGFjaXR5PSIwLjciLz4KICA8cmVjdCB4PSI5NTAiIHk9IjQwMCIgd2lkdGg9IjEyMCIgaGVpZ2h0PSIxNjAiIHJ4PSI4IiBmaWxsPSIjRkZGRkZGIiBvcGFjaXR5PSIwLjkiLz4KICA8cmVjdCB4PSI5NzAiIHk9IjQ5MCIgd2lkdGg9IjE1IiBoZWlnaHQ9IjQwIiBmaWxsPSIjNEE5MEUyIiBvcGFjaXR5PSIwLjgiLz4KICA8Y2lyY2xlIGN4PSIxMjAiIGN5PSI2NTAiIHI9IjgiIGZpbGw9IiNGRjhDNDIiIG9wYWNpdHk9IjAuNyIvPgo8L3N2Zz4=') center/cover fixed,
                linear-gradient(135deg, rgba(241, 241, 241, 0.85) 0%, rgba(232, 232, 232, 0.85) 100%);
        font-family: 'Montserrat', 'Open Sans', sans-serif;
        min-height: 100vh;
    }
    
    /* Main Content Area - Fixed Container Issues */
    .main .block-container {
        padding: 1rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        margin: 1rem auto;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(224, 60, 49, 0.1);
        max-width: 1200px;
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
    
    /* Fixed Login Container - No More White Block Issues */
    .login-container {
        max-width: 500px;
        margin: 2rem auto;
        padding: 3rem 2.5rem;
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(224, 60, 49, 0.2);
        border: 2px solid rgba(224, 60, 49, 0.15);
        position: relative;
        backdrop-filter: blur(15px);
        z-index: 10;
    }
    
    .login-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #E03C31, #FFB612);
        border-radius: 20px 20px 0 0;
    }
    
    /* Fix Text Color Issues in Login Form */
    .login-container * {
        color: #333333 !important;
    }
    
    .login-container h1, .login-container h2, .login-container h3 {
        color: #E03C31 !important;
    }
    
    .login-container p, .login-container div, .login-container span {
        color: #333333 !important;
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
    
    /* Fix Contrast Issues - Ensure All Text is Readable */
    .stApp * {
        color: #333333;
    }
    
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #E03C31 !important;
    }
    
    .stApp .stMarkdown p, .stApp .stMarkdown div, .stApp .stMarkdown span {
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
