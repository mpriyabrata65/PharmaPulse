import streamlit as st
import logging

logger = logging.getLogger(__name__)

def show_login_page():
    """Display the login page with enhanced PwC branding"""
    
    # Add background styling and header
    st.markdown("""
    <div class="fade-in">
        <h1 class="main-header">Welcome to Pharma Pulse</h1>
        <div style="text-align: center; margin-bottom: 2rem;">
            <p style="font-size: 1.2rem; color: #666; font-weight: 300;">
                Advanced PSUR Generation System
            </p>
            <hr class="pwc-divider">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container fade-in">', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h3 style="color: #E03C31; font-weight: 600;">🔐 User Authentication</h3>
            <p style="color: #666; font-size: 0.95rem;">Please enter your credentials to access the PSUR generation system</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form with enhanced styling
        with st.form("login_form"):
            st.markdown('<div style="margin: 1.5rem 0;">', unsafe_allow_html=True)
            username = st.text_input(
                "Username", 
                placeholder="Enter your username",
                help="Use 'admin' or 'reviewer' for demo access"
            )
            password = st.text_input(
                "Password", 
                type="password", 
                placeholder="Enter your secure password",
                help="Demo passwords: 'pwc@123' (admin) or 'review@123' (reviewer)"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                submit_button = st.form_submit_button("🚀 Secure Login", use_container_width=True)
        
        # Handle login
        if submit_button:
            auth_result = authenticate_user(username, password)
            if auth_result["authenticated"]:
                st.session_state.authenticated = True
                st.session_state.role = auth_result["role"]
                st.session_state.username = auth_result["username"]
                st.session_state.current_page = "📁 Data Upload"  # Set initial page to Data Upload
                logger.info(f"Successful login for user: {username} with role: {auth_result['role']}")
                st.success("✅ Login successful! Redirecting...")
                st.rerun()
            else:
                logger.warning(f"Failed login attempt for user: {username}")
                st.error("❌ Invalid username or password")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced Information section
        st.markdown('<hr class="pwc-divider">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #E03C31; margin-bottom: 1rem;">📋 System Information</h3>
            <p><strong>Pharma Pulse</strong> is a comprehensive PSUR generation system featuring:</p>
            <ul style="color: #333; line-height: 1.6;">
                <li>✅ Multi-source pharmaceutical data validation</li>
                <li>🤖 AI-powered PSUR reports (CDSCO compliant)</li>
                <li>📄 Professional Word and PDF export capabilities</li>
                <li>📊 Advanced data visualization and analytics</li>
                <li>🔒 Role-based access control system</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #E03C31; margin-bottom: 1rem;">🔑 Demo Credentials</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="padding: 1rem; background: rgba(224, 60, 49, 0.05); border-radius: 8px; border-left: 3px solid #E03C31;">
                    <h4 style="color: #E03C31; margin: 0 0 0.5rem 0;">Admin Access</h4>
                    <p style="margin: 0; font-family: monospace; font-size: 0.9rem;">
                        Username: <code>admin</code><br>
                        Password: <code>pwc@123</code>
                    </p>
                </div>
                <div style="padding: 1rem; background: rgba(255, 182, 18, 0.05); border-radius: 8px; border-left: 3px solid #FFB612;">
                    <h4 style="color: #FFB612; margin: 0 0 0.5rem 0;">Reviewer Access</h4>
                    <p style="margin: 0; font-family: monospace; font-size: 0.9rem;">
                        Username: <code>reviewer</code><br>
                        Password: <code>review@123</code>
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def authenticate_user(username: str, password: str) -> dict:
    """
    Authenticate user with hardcoded credentials and return role
    
    Args:
        username: Username entered by user
        password: Password entered by user
    
    Returns:
        dict: Contains 'authenticated' (bool) and 'role' (str) if successful, None if failed
    """
    
    # Hardcoded users and roles as specified
    USERS = {
        "admin": {"password": "pwc@123", "role": "admin"},
        "reviewer": {"password": "review@123", "role": "reviewer"}
    }
    
    if username in USERS and USERS[username]["password"] == password:
        return {
            "authenticated": True,
            "role": USERS[username]["role"],
            "username": username
        }
    
    return {"authenticated": False}
