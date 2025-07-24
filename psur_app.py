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
    
    # Sidebar navigation with clickable list
    st.sidebar.title("📊 Pharma Pulse")
    st.sidebar.markdown("---")
    
    # Initialize current page in session state if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "📄 Report Generation"
    
    # CSS for navigation styling
    st.markdown("""
    <style>
    /* Sidebar navigation styling */
    .nav-item {
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
        background: transparent;
        width: 100%;
        text-align: left;
        color: inherit;
        font-size: 0.9rem;
    }
    
    .nav-item:hover {
        background-color: #f0f2f6;
        color: #FF6600;
    }
    
    .nav-item.active {
        background-color: #FF6600;
        color: white;
        font-weight: 600;
    }
    
    .stButton > button {
        background-color: #FF6600 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: #e55a00 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Navigation menu with clickable buttons
    st.sidebar.markdown("**Navigation:**")
    
    # Data Upload page button
    if st.sidebar.button("📁 Data Upload", key="nav_data_upload", 
                        type="primary" if st.session_state.current_page == "📁 Data Upload" else "secondary",
                        use_container_width=True):
        st.session_state.current_page = "📁 Data Upload"
        st.rerun()
    
    # Report Generation page button
    if st.sidebar.button("📄 Report Generation", key="nav_report_gen",
                        type="primary" if st.session_state.current_page == "📄 Report Generation" else "secondary", 
                        use_container_width=True):
        st.session_state.current_page = "📄 Report Generation"
        st.rerun()
    
    # Account page button
    if st.sidebar.button("👤 Account", key="nav_account",
                        type="primary" if st.session_state.current_page == "👤 Account" else "secondary",
                        use_container_width=True):
        st.session_state.current_page = "👤 Account"
        st.rerun()
    
    # Logout section
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", type="secondary", use_container_width=True):
        logout()
    
    # Display current user info
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Logged in as:** admin")
    st.sidebar.markdown(f"**Session:** {datetime.now().strftime('%d-%b-%Y %H:%M')}")
    
    # Route to selected page based on session state
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
    st.session_state.current_page = "📄 Report Generation"  # Reset to default page
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
    """Display the PSUR report generation page"""
    
    # PWC Color styling with working Streamlit components
    st.markdown("""
    <style>
    /* PWC Brand Colors for working interface */
    .stButton > button {
        background-color: #FF6600 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        transition: background-color 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #e55a00 !important;
        color: white !important;
    }
    
    .stSelectbox > div > div {
        border-color: #FF6600 !important;
        border-radius: 4px !important;
    }
    
    .stDateInput > div > div > input {
        border-color: #FF6600 !important;
        border-radius: 4px !important;
    }
    
    .stSuccess {
        background-color: #E8F5E8 !important;
        border-left: 4px solid #4CAF50 !important;
        border-radius: 4px !important;
    }
    
    /* Date range container */
    .date-range-section {
        background-color: #F8F9FA;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #E5E5E5;
        margin: 1.5rem 0;
    }
    
    .date-header {
        color: #2B5D42;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    .date-label-custom {
        color: #2C3E50;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📄 PSUR Report Generation")
    
    # Check if data is uploaded
    if not st.session_state.uploaded_data:
        st.warning("⚠️ Please upload and validate data files first before generating reports.")
        return
    
    st.success(f"✅ Data loaded for {len(st.session_state.uploaded_data)} datasets")
    
    # Product selection
    products_df = st.session_state.uploaded_data.get('Products.csv')
    if products_df is not None and not products_df.empty:
        
        st.markdown("### 🎯 Select Product for PSUR Generation")
        
        # Product selection dropdown
        product_options = products_df[['ProductID', 'ProductName']].apply(
            lambda row: f"{row['ProductID']} - {row['ProductName']}", axis=1
        ).tolist()
        
        selected_product = st.selectbox(
            "Choose a product:",
            options=product_options,
            help="Select the product for which you want to generate a PSUR report"
        )
        
        if selected_product:
            product_id = selected_product.split(' - ')[0]
            
            # Date Range Selection Section - PWC styled
            st.markdown('<div class="date-range-section">', unsafe_allow_html=True)
            st.markdown('<div class="date-header">📅 Report Date Range</div>', unsafe_allow_html=True)
            
            # Create two columns for start and end dates
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="date-label-custom">Start Date</div>', unsafe_allow_html=True)
                # Default to 1 year ago
                default_start = datetime.now() - timedelta(days=365)
                start_date = st.date_input(
                    "Start date for PSUR period",
                    value=default_start,
                    key="start_date",
                    help="Select the start date for the PSUR reporting period",
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown('<div class="date-label-custom">End Date</div>', unsafe_allow_html=True)
                # Default to today
                default_end = datetime.now()
                end_date = st.date_input(
                    "End date for PSUR period",
                    value=default_end,
                    key="end_date",
                    help="Select the end date for the PSUR reporting period",
                    label_visibility="collapsed"
                )
            
            # Validate date range
            if start_date > end_date:
                st.error("⚠️ Start date must be before end date")
            else:
                # Show selected date range
                st.success(f"📊 **Report Period:** {start_date.strftime('%d-%b-%Y')} to {end_date.strftime('%d-%b-%Y')}")
                
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
            
            # Generate report button - only show if date range is valid
            if start_date <= end_date:
                if st.button("🤖 Generate PSUR Report", type="primary"):
                    with st.spinner("Generating AI-powered PSUR report..."):
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
                            st.success("✅ PSUR report generated successfully!")
                            
                        except Exception as e:
                            logger.error(f"Error generating report: {str(e)}")
                            st.error(f"❌ Error generating report: {str(e)}")
            
            # Display generated report
            if 'generated_report' in st.session_state:
                display_generated_report()
    
    else:
        st.error("❌ No products data available. Please check your uploaded files.")

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
