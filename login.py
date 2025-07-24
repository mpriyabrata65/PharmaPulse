import streamlit as st
import logging

logger = logging.getLogger(__name__)

def show_login_page():
    """Display the login page with PwC branding"""
    
    # Main header
    st.markdown('<h1 class="main-header">Welcome to Pharma Pulse</h1>', unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown("### 🔐 User Authentication")
        st.markdown("Please enter your credentials to access the PSUR generation system.")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                submit_button = st.form_submit_button("🚀 Login", use_container_width=True)
        
        # Handle login
        if submit_button:
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.current_page = "📁 Data Upload"  # Set initial page to Data Upload
                st.session_state.username = username
                logger.info(f"Successful login for user: {username}")
                st.success("✅ Login successful! Redirecting...")
                st.rerun()
            else:
                logger.warning(f"Failed login attempt for user: {username}")
                st.error("❌ Invalid username or password")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Information section
        st.markdown("---")
        st.markdown("### 📋 System Information")
        st.info("""
        **Pharma Pulse** is a comprehensive PSUR generation system that:
        - Validates pharmaceutical data from multiple sources
        - Generates AI-powered PSUR reports compliant with CDSCO standards
        - Exports reports in Word and PDF formats
        - Provides data visualization and analytics
        """)
        
        st.markdown("### 🔑 Default Credentials")
        st.markdown("**Username:** `admin`")
        st.markdown("**Password:** `pwc@123`")

def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate user with hardcoded credentials
    
    Args:
        username: Username entered by user
        password: Password entered by user
    
    Returns:
        bool: True if authentication successful, False otherwise
    """
    
    # Hardcoded credentials as specified
    VALID_USERNAME = "admin"
    VALID_PASSWORD = "pwc@123"
    
    return username == VALID_USERNAME and password == VALID_PASSWORD
