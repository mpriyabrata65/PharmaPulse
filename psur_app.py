import streamlit as st
import pandas as pd
import logging
from datetime import datetime, timedelta
import os

# Import our modules
import backend
import report_generator
import docx_pdf_exporter
import utils

logger = logging.getLogger(__name__)

def main_app():
    """Main application after successful login"""
    
    # Apply the exact UI styling from the reference image with PWC colors
    st.markdown("""
    <style>
    /* Reset and base styling to match reference image */
    .main > div {
        padding: 0 !important;
        max-width: none !important;
    }
    
    /* Sidebar styling - dark green like in reference */
    .css-1d391kg {
        background-color: #2B5D42 !important;
        border-right: 1px solid #1e3e2b !important;
    }
    
    .sidebar .sidebar-content {
        background-color: #2B5D42 !important;
        padding: 0 !important;
    }
    
    /* Sidebar navigation items */
    .css-17eq0hr {
        background-color: #2B5D42 !important;
        color: white !important;
    }
    
    .css-1v0mbdj .block-container {
        padding: 0 !important;
    }
    
    /* Sidebar text styling */
    .sidebar .sidebar-content .element-container {
        color: white !important;
    }
    
    .sidebar .sidebar-content h1 {
        color: white !important;
        font-size: 1.2rem !important;
        padding: 1rem !important;
        margin: 0 !important;
        background-color: #1e3e2b !important;
    }
    
    /* Sidebar buttons */
    .sidebar .stButton button {
        background-color: transparent !important;
        color: white !important;
        border: none !important;
        text-align: left !important;
        width: 100% !important;
        padding: 0.75rem 1rem !important;
        border-radius: 0 !important;
        font-weight: normal !important;
    }
    
    .sidebar .stButton button:hover {
        background-color: #3a7259 !important;
        color: white !important;
    }
    
    /* Sidebar selectbox styling */
    .sidebar .stSelectbox > div > div {
        background-color: transparent !important;
        border: 1px solid #3a7259 !important;
        color: white !important;
    }
    
    .sidebar .stSelectbox label {
        color: white !important;
        font-weight: normal !important;
    }
    
    /* Main content area - clean white like reference */
    .main .main-content {
        background-color: #ffffff !important;
        padding: 2rem !important;
        min-height: 100vh !important;
    }
    
    /* Top header bar like in reference */
    .top-header {
        background-color: #ffffff;
        padding: 1rem 2rem;
        border-bottom: 1px solid #e0e0e0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .user-info {
        display: flex;
        align-items: center;
        gap: 1rem;
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Page title styling */
    .page-title {
        color: #2B5D42;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #FF6600;
        display: inline-block;
    }
    
    /* Content sections */
    .content-section {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    /* PWC Orange accent buttons */
    .primary-button {
        background-color: #FF6600 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: background-color 0.3s ease !important;
    }
    
    .primary-button:hover {
        background-color: #e55a00 !important;
    }
    
    /* Secondary button styling */
    .secondary-button {
        background-color: transparent !important;
        color: #2B5D42 !important;
        border: 2px solid #2B5D42 !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
    }
    
    .secondary-button:hover {
        background-color: #2B5D42 !important;
        color: white !important;
    }
    
    /* Form input styling */
    .stSelectbox > div > div, .stDateInput > div > div > input {
        border: 1px solid #d0d0d0 !important;
        border-radius: 4px !important;
        padding: 0.75rem !important;
        font-size: 0.9rem !important;
    }
    
    .stSelectbox > div > div:focus-within, .stDateInput > div > div > input:focus {
        border-color: #FF6600 !important;
        box-shadow: 0 0 0 2px rgba(255, 102, 0, 0.2) !important;
    }
    
    /* Toggle switch styling like in reference */
    .stCheckbox > label {
        color: #333 !important;
        font-weight: 500 !important;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #E8F5E8 !important;
        border-left: 4px solid #4CAF50 !important;
        border-radius: 4px !important;
        color: #2E7D2E !important;
    }
    
    /* Date range specific styling to match reference */
    .date-range-container {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .date-range-header {
        color: #2B5D42;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .date-field-label {
        color: #666;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom navigation menu */
    .nav-menu {
        background-color: #2B5D42;
        padding: 0;
        margin: 0;
    }
    
    .nav-item {
        color: white;
        padding: 1rem;
        cursor: pointer;
        border-bottom: 1px solid #3a7259;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 0.9rem;
    }
    
    .nav-item:hover {
        background-color: #3a7259;
    }
    
    .nav-item.active {
        background-color: #FF6600;
        border-left: 4px solid #e55a00;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Custom sidebar navigation to match reference image
    with st.sidebar:
        st.markdown('<div class="nav-menu">', unsafe_allow_html=True)
        
        # Dashboard header
        st.markdown("""
        <div style="background-color: #1e3e2b; padding: 1rem; color: white; font-weight: 600;">
            📊 Dashboard
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation items
        page_options = {
            "📁 Data Upload": "📁 Solicitudes",
            "📄 Report Generation": "📄 Reportes", 
            "👤 Account": "👤 Perfil"
        }
        
        selected_page = None
        for key, display_name in page_options.items():
            if st.button(display_name, key=f"nav_{key}", use_container_width=True):
                selected_page = key
        
        # Set default page if none selected
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "📄 Report Generation"
        
        if selected_page:
            st.session_state.current_page = selected_page
        
        # Bottom section - user info and logout
        st.markdown("---")
        st.markdown("**Usuario:** FullName")
        
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            logout()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area with top header
    st.markdown("""
    <div class="top-header">
        <div class="user-info">
            <span>🇺🇸 EN</span>
            <span>👤 FullName</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Route to selected page
    if st.session_state.current_page == "📁 Data Upload":
        show_data_upload_page()
    elif st.session_state.current_page == "📄 Report Generation":
        show_report_generation_page()
    elif st.session_state.current_page == "👤 Account":
        show_account_page()

def logout():
    """Handle user logout"""
    st.session_state.authenticated = False
    st.session_state.uploaded_data = {}
    st.session_state.validation_results = {}
    logger.info("User logged out")
    st.rerun()

def show_data_upload_page():
    """Display the data upload and validation page"""
    
    st.markdown('<h1 class="main-header">📁 Data Upload & Validation</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Upload the six required CSV files for PSUR generation. Each file will be validated against 
    the required schema before processing.
    """)
    
    # Required files information
    with st.expander("📋 Required File Schemas", expanded=False):
        st.markdown("""
        **1. Products.csv:** ProductID, ProductName, INN, DosageForm, Strength
        
        **2. Authorizations.csv:** AuthorizationID, ProductID, Country, MarketingStatus, AuthorizationDate, LicenseNumber
        
        **3. AdverseEvents.csv:** AEID, ProductID, ReportedDate, PatientAge, Gender, EventDescription, Outcome
        
        **4. RegulatoryActions.csv:** ActionID, ProductID, ActionDate, Region, ActionTaken, Justification
        
        **5. ExposureEstimates.csv:** ExposureID, ProductID, Region, TimePeriod, EstimatedPatients, EstimationMethod
        
        **6. ClinicalStudies.csv:** StudyID, ProductID, StudyTitle, Status, CompletionDate
        """)
    
    # File upload section
    st.markdown("### 📤 Upload Files")
    
    uploaded_files = {}
    file_names = [
        "Products.csv",
        "Authorizations.csv", 
        "AdverseEvents.csv",
        "RegulatoryActions.csv",
        "ExposureEstimates.csv",
        "ClinicalStudies.csv"
    ]
    
    # Create upload widgets for each file
    cols = st.columns(2)
    for i, file_name in enumerate(file_names):
        with cols[i % 2]:
            uploaded_file = st.file_uploader(
                f"📊 {file_name}",
                type=['csv'],
                key=f"upload_{file_name}"
            )
            if uploaded_file is not None:
                uploaded_files[file_name] = uploaded_file
    
    # Validation and processing
    if uploaded_files:
        st.markdown("### 🔍 Validation Results")
        
        if st.button("🚀 Validate All Files", type="primary"):
            with st.spinner("Validating uploaded files..."):
                validation_results = backend.validate_all_files(uploaded_files)
                st.session_state.validation_results = validation_results
                
                # Display validation results
                display_validation_results(validation_results)
                
                # If all validations pass, store data
                if all(result['valid'] for result in validation_results.values()):
                    st.session_state.uploaded_data = backend.process_validated_files(uploaded_files)
                    st.success("✅ All files validated successfully! You can now proceed to report generation.")
                    logger.info("All files validated successfully")
        
        # Display previous validation results if available
        if st.session_state.validation_results:
            display_validation_results(st.session_state.validation_results)

def display_validation_results(validation_results):
    """Display validation results in a user-friendly format"""
    
    for file_name, result in validation_results.items():
        if result['valid']:
            st.success(f"✅ {file_name}: Valid ({result['rows']} rows)")
        else:
            st.error(f"❌ {file_name}: Invalid")
            for error in result['errors']:
                st.error(f"   • {error}")

def show_report_generation_page():
    """Display the PSUR report generation page exactly like the reference image"""
    
    # Page title matching reference
    st.markdown('<div class="page-title">Reportes</div>', unsafe_allow_html=True)
    
    # Main content section like in reference
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #2B5D42; font-size: 1.4rem; margin-bottom: 1.5rem;">Generar reporte</h2>', unsafe_allow_html=True)
    
    # Check if data is uploaded
    if not st.session_state.uploaded_data:
        st.markdown("""
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 1rem; color: #856404; margin: 1rem 0;">
            ⚠️ Please upload and validate data files first before generating reports.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Product type selection (matching reference layout)
    st.markdown('<div class="date-field-label">Tipo de reporte</div>', unsafe_allow_html=True)
    
    # Product selection
    products_df = st.session_state.uploaded_data.get('Products.csv')
    if products_df is not None and not products_df.empty:
        
        # Product selection dropdown
        product_options = products_df[['ProductID', 'ProductName']].apply(
            lambda row: f"{row['ProductID']} - {row['ProductName']}", axis=1
        ).tolist()
        
        selected_product = st.selectbox(
            "Select product type",
            options=["Select"] + product_options,
            label_visibility="collapsed"
        )
        
        if selected_product and selected_product != "Select":
            product_id = selected_product.split(' - ')[0]
            
            # Date range toggle (exactly like reference)
            st.markdown('<div style="margin: 1.5rem 0;">', unsafe_allow_html=True)
            st.markdown('<div class="date-field-label">Reporte por rango de fecha</div>', unsafe_allow_html=True)
            
            # Toggle switch
            date_range_enabled = st.toggle("", value=True, key="date_range_toggle")
            
            if date_range_enabled:
                # Date Range Selection Section - exactly like reference layout
                st.markdown('<div class="date-range-container">', unsafe_allow_html=True)
                
                # Create two columns for start and end dates exactly like reference
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="date-field-label">Fecha inicio</div>', unsafe_allow_html=True)
                    # Default to 1 year ago
                    default_start = datetime.now() - timedelta(days=365)
                    start_date = st.date_input(
                        "Start date",
                        value=default_start,
                        key="start_date",
                        format="YYYY/MM/DD",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    st.markdown('<div class="date-field-label">Fecha final</div>', unsafe_allow_html=True)
                    # Default to today
                    default_end = datetime.now()
                    end_date = st.date_input(
                        "End date",
                        value=default_end,
                        key="end_date",
                        format="YYYY/MM/DD",
                        label_visibility="collapsed"
                    )
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # Use current date if toggle is off
                start_date = datetime.now() - timedelta(days=365)
                end_date = datetime.now()
            
            # Store dates in session state
            st.session_state.report_start_date = start_date
            st.session_state.report_end_date = end_date
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Debug information
            with st.expander("🔍 Debug Information", expanded=False):
                st.markdown("**Product Data Summary:**")
                product_debug_data = backend.get_product_data(product_id, st.session_state.uploaded_data)
                for file_name, df in product_debug_data.items():
                    st.markdown(f"- **{file_name}:** {len(df) if df is not None else 0} rows")
                    if df is not None and len(df) > 0:
                        st.dataframe(df.head(3))
            
            # Action buttons exactly like reference layout
            st.markdown('<div style="margin: 2rem 0; display: flex; gap: 1rem;">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                clear_button = st.button("Limpiar", key="clear_btn", use_container_width=True)
            with col2:
                generate_button = st.button("Generar reporte", key="generate_btn", use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Only proceed if generate button clicked and date range is valid
            if generate_button and start_date <= end_date:
                with st.spinner("Generando reporte PSUR..."):
                        try:
                            # Debug: Show what data is being passed
                            debug_data = backend.get_product_data(product_id, st.session_state.uploaded_data)
                            logger.info(f"Generating report for product {product_id} with data: {[(k, len(v) if v is not None else 0) for k, v in debug_data.items()]}")
                            
                            # Generate the report
                            report_content = report_generator.generate_psur_report(
                                product_id, 
                                st.session_state.uploaded_data
                            )
                            
                            st.session_state.generated_report = report_content
                            st.session_state.report_product_id = product_id
                            
                            logger.info(f"PSUR report generated for product: {product_id}")
                            st.markdown("""
                            <div style="background-color: #E8F5E8; border: 1px solid #4CAF50; border-radius: 4px; padding: 1rem; color: #2E7D2E; margin: 1rem 0;">
                                ✅ Reporte PSUR generado exitosamente
                            </div>
                            """, unsafe_allow_html=True)
                            
                        except Exception as e:
                            logger.error(f"Error generating report: {str(e)}")
                            st.markdown(f"""
                            <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; padding: 1rem; color: #721c24; margin: 1rem 0;">
                                ❌ Error generando reporte: {str(e)}
                            </div>
                            """, unsafe_allow_html=True)
            
            elif clear_button:
                # Clear form functionality
                st.rerun()
            
            # Display generated report
            if 'generated_report' in st.session_state:
                display_generated_report()
    
    else:
        st.markdown("""
        <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; padding: 1rem; color: #721c24; margin: 1rem 0;">
            ❌ No hay datos de productos disponibles. Por favor verifique sus archivos cargados.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close content section

def display_generated_report():
    """Display the generated PSUR report with download options"""
    
    st.markdown("### 📋 Generated PSUR Report")
    
    # Display report content
    with st.expander("📖 View Report Content", expanded=True):
        st.markdown(st.session_state.generated_report, unsafe_allow_html=True)
    
    # Export options
    st.markdown("### 📥 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download as Word (.docx)", type="secondary"):
            try:
                docx_file = docx_pdf_exporter.generate_docx(
                    st.session_state.generated_report,
                    st.session_state.report_product_id
                )
                
                with open(docx_file, "rb") as file:
                    st.download_button(
                        label="⬇️ Download DOCX",
                        data=file.read(),
                        file_name=f"PSUR_Report_{st.session_state.report_product_id}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                logger.info(f"DOCX report generated for product: {st.session_state.report_product_id}")
                
            except Exception as e:
                logger.error(f"Error generating DOCX: {str(e)}")
                st.error(f"❌ Error generating DOCX: {str(e)}")
    
    with col2:
        if st.button("📄 Download as PDF", type="secondary"):
            try:
                pdf_file = docx_pdf_exporter.generate_pdf(
                    st.session_state.generated_report,
                    st.session_state.report_product_id
                )
                
                with open(pdf_file, "rb") as file:
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=file.read(),
                        file_name=f"PSUR_Report_{st.session_state.report_product_id}.pdf",
                        mime="application/pdf"
                    )
                logger.info(f"PDF report generated for product: {st.session_state.report_product_id}")
                
            except Exception as e:
                logger.error(f"Error generating PDF: {str(e)}")
                st.error(f"❌ Error generating PDF: {str(e)}")
    
    # Optional data visualization section
    show_data_visualization()

def show_data_visualization():
    """Show optional data visualization section"""
    
    with st.expander("📊 Data Analytics & Visualization", expanded=False):
        if st.session_state.uploaded_data:
            
            # Adverse Events Summary
            ae_df = st.session_state.uploaded_data.get('AdverseEvents.csv')
            if ae_df is not None and not ae_df.empty:
                st.markdown("#### 📈 Adverse Events Summary")
                
                # Filter for current product
                if 'report_product_id' in st.session_state:
                    product_ae = ae_df[ae_df['ProductID'] == st.session_state.report_product_id]
                    
                    if not product_ae.empty:
                        # Outcome distribution
                        outcome_counts = product_ae['Outcome'].value_counts()
                        st.bar_chart(outcome_counts)
                        
                        # Summary table
                        st.dataframe(outcome_counts.reset_index())
                    else:
                        st.info("No adverse events data available for this product.")
            
            # Exposure Estimates Summary
            exposure_df = st.session_state.uploaded_data.get('ExposureEstimates.csv')
            if exposure_df is not None and not exposure_df.empty:
                st.markdown("#### 📊 Exposure Estimates by Region")
                
                if 'report_product_id' in st.session_state:
                    product_exposure = exposure_df[exposure_df['ProductID'] == st.session_state.report_product_id]
                    
                    if not product_exposure.empty:
                        # Regional exposure chart
                        regional_exposure = product_exposure.groupby('Region')['EstimatedPatients'].sum().reset_index()
                        st.bar_chart(regional_exposure.set_index('Region'))
                        
                        # Summary table
                        st.dataframe(regional_exposure)
                    else:
                        st.info("No exposure estimates data available for this product.")

def show_account_page():
    """Display account information and settings"""
    
    st.markdown('<h1 class="main-header">👤 Account Information</h1>', unsafe_allow_html=True)
    
    # User information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 User Profile")
        st.info("""
        **Username:** admin  
        **Role:** PSUR Administrator  
        **Access Level:** Full Access  
        **Department:** Pharmacovigilance  
        """)
    
    with col2:
        st.markdown("### 📊 Session Statistics")
        uploaded_files_count = len(st.session_state.uploaded_data)
        
        st.metric("Uploaded Datasets", uploaded_files_count)
        st.metric("Generated Reports", 1 if 'generated_report' in st.session_state else 0)
    
    # System information
    st.markdown("### ⚙️ System Information")
    st.info("""
    **Application:** Pharma Pulse v1.0  
    **Compliance:** Indian CDSCO Standards  
    **Framework:** ICH E2C(R2)  
    **AI Model:** OpenAI GPT-4o  
    """)
    
    # Clear session data
    st.markdown("### 🧹 Session Management")
    if st.button("🗑️ Clear All Data", type="secondary"):
        st.session_state.uploaded_data = {}
        st.session_state.validation_results = {}
        if 'generated_report' in st.session_state:
            del st.session_state.generated_report
        if 'report_product_id' in st.session_state:
            del st.session_state.report_product_id
        st.success("✅ All session data cleared successfully!")
        st.rerun()
