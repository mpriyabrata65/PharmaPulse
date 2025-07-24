import streamlit as st
import pandas as pd
import logging
from datetime import datetime
import os

# Import our modules
import backend
import report_generator
import docx_pdf_exporter
import utils

logger = logging.getLogger(__name__)

def main_app():
    """Main application after successful login"""
    
    # Sidebar navigation
    st.sidebar.title("📊 Pharma Pulse")
    st.sidebar.markdown("---")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["📁 Data Upload", "📄 Report Generation", "👤 Account"]
    )
    
    # Logout button
    if st.sidebar.button("🚪 Logout", type="secondary"):
        logout()
    
    # Display current user
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Logged in as:** admin")
    st.sidebar.markdown(f"**Session started:** {datetime.now().strftime('%d-%b-%Y %H:%M')}")
    
    # Route to selected page
    if page == "📁 Data Upload":
        show_data_upload_page()
    elif page == "📄 Report Generation":
        show_report_generation_page()
    elif page == "👤 Account":
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
    """Display the PSUR report generation page"""
    
    st.markdown('<h1 class="main-header">📄 PSUR Report Generation</h1>', unsafe_allow_html=True)
    
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
            
            # Generate report button
            if st.button("🤖 Generate PSUR Report", type="primary"):
                with st.spinner("Generating AI-powered PSUR report..."):
                    try:
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
