import streamlit as st
import logging

logger = logging.getLogger(__name__)

def show_login_page():
    """Display the login page with enhanced PwC branding"""
    
    # Apply login page with pharmaceutical elements inspired by reference images
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #F8F8F8 0%, #FFFFFF 100%) !important;
        position: relative;
        min-height: 100vh;
    }
    
    /* Grid Pattern Background (like medical chart paper) */
    .stApp::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            linear-gradient(rgba(224, 60, 49, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(224, 60, 49, 0.05) 1px, transparent 1px);
        background-size: 20px 20px;
        z-index: 0;
        pointer-events: none;
    }
    
    /* Pharmaceutical Pills as Chart Elements */
    .stApp::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
            /* Red Pills (PwC Red) - forming chart bars */
            radial-gradient(ellipse 12px 8px at 15% 75%, rgba(224, 60, 49, 0.15), transparent 70%),
            radial-gradient(ellipse 10px 6px at 20% 70%, rgba(224, 60, 49, 0.12), transparent 70%),
            radial-gradient(ellipse 14px 9px at 25% 65%, rgba(224, 60, 49, 0.18), transparent 70%),
            radial-gradient(ellipse 16px 10px at 30% 55%, rgba(224, 60, 49, 0.20), transparent 70%),
            
            /* Yellow/Orange Pills (PwC Yellow) - forming ascending chart */
            radial-gradient(ellipse 10px 6px at 70% 80%, rgba(255, 182, 18, 0.15), transparent 70%),
            radial-gradient(ellipse 12px 8px at 75% 75%, rgba(255, 182, 18, 0.18), transparent 70%),
            radial-gradient(ellipse 14px 9px at 80% 68%, rgba(255, 182, 18, 0.20), transparent 70%),
            radial-gradient(ellipse 16px 10px at 85% 58%, rgba(255, 182, 18, 0.22), transparent 70%),
            
            /* Prescription Bottles - vertical chart elements */
            linear-gradient(to top, rgba(224, 60, 49, 0.08) 0%, transparent 15%) 10% 85%/6px 40px no-repeat,
            linear-gradient(to top, rgba(255, 182, 18, 0.10) 0%, transparent 20%) 15% 80%/6px 50px no-repeat,
            linear-gradient(to top, rgba(224, 60, 49, 0.12) 0%, transparent 25%) 20% 75%/6px 60px no-repeat,
            linear-gradient(to top, rgba(255, 182, 18, 0.14) 0%, transparent 30%) 25% 70%/6px 70px no-repeat,
            
            /* Capsules scattered like data points */
            radial-gradient(ellipse 8px 4px at 45% 25%, rgba(224, 60, 49, 0.08), transparent 70%),
            radial-gradient(ellipse 6px 3px at 55% 30%, rgba(255, 182, 18, 0.08), transparent 70%),
            radial-gradient(ellipse 10px 5px at 40% 35%, rgba(224, 60, 49, 0.06), transparent 70%),
            
            /* Medical cross symbols */
            linear-gradient(rgba(224, 60, 49, 0.04), rgba(224, 60, 49, 0.04)) 85% 20%/12px 2px no-repeat,
            linear-gradient(rgba(224, 60, 49, 0.04), rgba(224, 60, 49, 0.04)) 85% 20%/2px 12px no-repeat,
            linear-gradient(rgba(255, 182, 18, 0.04), rgba(255, 182, 18, 0.04)) 90% 85%/12px 2px no-repeat,
            linear-gradient(rgba(255, 182, 18, 0.04), rgba(255, 182, 18, 0.04)) 90% 85%/2px 12px no-repeat;
        z-index: 0;
        pointer-events: none;
    }
    
    .main .block-container {
        position: relative;
        z-index: 1;
        background: rgba(255, 255, 255, 0.96) !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 32px rgba(224, 60, 49, 0.12) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(224, 60, 49, 0.08) !important;
        margin: 2rem auto !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Clean header without extra boxes
    st.markdown("""
    <div class="fade-in" style="text-align: center;">
        <h1 class="main-header">Welcome to Pharma Pulse</h1>
        <p style="font-size: 1.2rem; color: #666; font-weight: 300; margin: 0 0 2rem 0;">
            Advanced PSUR Generation System
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the login form without white container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <h3 style="color: #E03C31; font-weight: 600; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);">🔐 User Authentication</h3>
            <p style="color: #444; font-size: 0.95rem; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);">Please enter your credentials to access the PSUR generation system</p>
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
        
        # Enhanced Information section with transparent background
        st.markdown('<hr style="border: 1px solid rgba(224, 60, 49, 0.3); margin: 2rem 0;">', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.2); border-radius: 10px; backdrop-filter: blur(5px);">
            <h3 style="color: #E03C31; margin-bottom: 1rem; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);">📋 System Information</h3>
            <p style="color: #444; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);"><strong>Pharma Pulse</strong> is a comprehensive PSUR generation system featuring:</p>
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
