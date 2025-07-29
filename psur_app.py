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
        st.session_state.current_page = "📁 Data Upload"
    
    # CSS for navigation styling
    st.markdown("""
    <style>
    /* Navigation styling */
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
    
    # Navigation menu with role-based access
    st.sidebar.markdown("**Navigation:**")
    
    user_role = st.session_state.get('role', '')
    
    # Data Upload page button (Admin only)
    if user_role == 'admin':
        if st.sidebar.button("📁 Data Upload", key="nav_data_upload", 
                            type="primary" if st.session_state.current_page == "📁 Data Upload" else "secondary",
                            use_container_width=True):
            st.session_state.current_page = "📁 Data Upload"
            st.rerun()
    
    # Report Generation page button (Both admin and reviewer, but with different access levels)
    if st.sidebar.button("📄 Report Generation", key="nav_report_gen",
                        type="primary" if st.session_state.current_page == "📄 Report Generation" else "secondary", 
                        use_container_width=True):
        st.session_state.current_page = "📄 Report Generation"
        st.rerun()
    
    # Account page button (Both roles)
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
    user_role = st.session_state.get('role', 'Unknown')
    username = st.session_state.get('username', 'Unknown')
    st.sidebar.markdown(f"**Logged in as:** {username}")
    st.sidebar.markdown(f"**Role:** {user_role.title()}")
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
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.uploaded_data = {}
    st.session_state.validation_results = {}
    st.session_state.current_page = "📁 Data Upload"  # Reset to default page
    logger.info("User logged out")
    st.rerun()

def show_data_upload_page():
    """Display the data upload and validation page"""
    
    st.markdown('<h1 class="main-header">📁 Data Upload & Validation</h1>', unsafe_allow_html=True)
    
    # Check user role for access control
    user_role = st.session_state.get('role', '')
    
    if user_role == 'reviewer':
        st.info("Reviewer access: Upload and report generation disabled.")
        st.markdown("""
        As a reviewer, you can only view previously generated reports. 
        Upload and report generation features are restricted to admin users.
        """)
        return
    
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
    
    # Check user role for access control
    user_role = st.session_state.get('role', '')
    
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
    
    # Role-based access control for report generation
    if user_role == 'reviewer':
        st.info("Reviewer access: Upload and report generation disabled.")
        
        # Show only report preview and download if report exists
        if 'generated_report' in st.session_state:
            st.markdown("### 📋 Available Report")
            display_generated_report()
        else:
            st.markdown("""
            No reports are currently available for preview. 
            Reports can only be generated by admin users.
            """)
        return
    
    # Check if data is uploaded (admin only)
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
                            
                            # Load existing reviewer notes for this product
                            load_reviewer_notes_from_file(product_id)
                            
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
    
    # Get current user role
    user_role = st.session_state.get('role', '')
    
    # Determine what content to display (edited or original)
    display_content = st.session_state.get('edited_report_content') or st.session_state.generated_report
    
    # Display report content
    with st.expander("📖 View Report Content", expanded=True):
        st.markdown(display_content, unsafe_allow_html=True)
    
    # Admin-only reviewer notes and editing section
    if user_role == 'admin':
        show_admin_editing_section()
    
    # Export options
    st.markdown("### 📥 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download as Word (.docx)", type="secondary"):
            try:
                # Use final report content with edits and notes
                final_content = get_final_report_content()
                docx_file = docx_pdf_exporter.generate_docx(
                    final_content,
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
                # Use final report content with edits and notes
                final_content = get_final_report_content()
                pdf_file = docx_pdf_exporter.generate_pdf(
                    final_content,
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

def show_admin_editing_section():
    """Display admin-only editing and reviewer notes section"""
    
    with st.expander("✍️ Reviewer Notes & Final Edits"):
        st.markdown("### 🗒️ Add Reviewer Note")
        
        # Add new reviewer note
        new_note = st.text_area(
            "Enter your comments here:",
            placeholder="Add notes about the review process, changes needed, or final remarks...",
            height=100,
            key="new_reviewer_note"
        )
        
        if st.button("➕ Add Note", type="secondary"):
            if new_note.strip():
                # Get current product ID
                product_id = st.session_state.get('report_product_id', 'default')
                
                # Initialize notes for this product if not exists
                if product_id not in st.session_state.reviewer_notes:
                    st.session_state.reviewer_notes[product_id] = []
                
                # Create note entry with timestamp
                from datetime import datetime
                note_entry = {
                    "timestamp": datetime.now().strftime('%d-%b-%Y %H:%M'),
                    "author": st.session_state.get('username', 'admin'),
                    "note": new_note.strip()
                }
                
                # Add to notes list
                st.session_state.reviewer_notes[product_id].append(note_entry)
                
                # Save notes to file
                save_reviewer_notes_to_file(product_id)
                
                st.success("✅ Note added successfully!")
                st.rerun()
        
        # Display notes history
        product_id = st.session_state.get('report_product_id', 'default')
        if product_id in st.session_state.reviewer_notes and st.session_state.reviewer_notes[product_id]:
            st.markdown("### 📝 Reviewer Notes History")
            
            # Display notes in reverse chronological order (newest first)
            notes = st.session_state.reviewer_notes[product_id]
            for note in reversed(notes):
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #E03C31;">
                    <div style="color: #666; font-size: 0.9rem; margin-bottom: 5px;">
                        🕒 <strong>{note['timestamp']}</strong> – {note['author']}
                    </div>
                    <div style="color: #333;">
                        "{note['note']}"
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Edit PSUR content section
        st.markdown("### ✏️ Edit PSUR Content")
        
        edit_mode = st.checkbox("Edit PSUR content before finalizing", key="edit_psur_checkbox")
        
        if edit_mode:
            st.markdown("**Edit the PSUR report content below:**")
            
            # Get current content (edited or original)
            current_content = st.session_state.get('edited_report_content') or st.session_state.generated_report
            
            edited_content = st.text_area(
                "Edit PSUR Report:",
                value=current_content,
                height=400,
                key="psur_editor",
                help="Make any necessary changes to the PSUR report content. This will be included in the final downloads."
            )
            
            # Update edited content in session state
            st.session_state.edited_report_content = edited_content
        
        # Final reviewer notes for the report
        st.markdown("### 📄 Final Reviewer Comments")
        final_notes = st.text_area(
            "Final comments to include in the report:",
            value=st.session_state.get('final_reviewer_notes', ''),
            placeholder="Enter final reviewer comments that will be appended to the report...",
            height=100,
            key="final_reviewer_comments"
        )
        
        # Update final notes in session state
        st.session_state.final_reviewer_notes = final_notes
        
        # Finalize button
        if st.button("📋 Finalize & Update Report", type="primary"):
            st.success("✅ Report finalized with your edits and notes!")
            st.info("Your changes will be included in the download files.")

def save_reviewer_notes_to_file(product_id):
    """Save reviewer notes to a JSON file"""
    import json
    import os
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        # File path for notes
        notes_file = f"output/reviewer_notes_{product_id}.json"
        
        # Get notes for this product
        notes = st.session_state.reviewer_notes.get(product_id, [])
        
        # Save to file
        with open(notes_file, 'w') as f:
            json.dump(notes, f, indent=2)
            
        logger.info(f"Reviewer notes saved to {notes_file}")
        
    except Exception as e:
        logger.error(f"Error saving reviewer notes: {str(e)}")

def load_reviewer_notes_from_file(product_id):
    """Load reviewer notes from JSON file if exists"""
    import json
    import os
    
    try:
        notes_file = f"output/reviewer_notes_{product_id}.json"
        
        if os.path.exists(notes_file):
            with open(notes_file, 'r') as f:
                notes = json.load(f)
                
            # Initialize if not exists
            if product_id not in st.session_state.reviewer_notes:
                st.session_state.reviewer_notes[product_id] = []
            
            # Load notes into session state
            st.session_state.reviewer_notes[product_id] = notes
            logger.info(f"Reviewer notes loaded from {notes_file}")
            
    except Exception as e:
        logger.error(f"Error loading reviewer notes: {str(e)}")

def get_final_report_content():
    """Get the final report content including edits and reviewer notes"""
    
    # Get the content (edited or original)
    content = st.session_state.get('edited_report_content') or st.session_state.generated_report
    
    # Add final reviewer notes if they exist
    final_notes = st.session_state.get('final_reviewer_notes', '').strip()
    if final_notes:
        content += f"\n\n## Reviewer Comments & Final Remarks\n\n{final_notes}"
    
    # Add notes history if in admin mode and notes exist
    user_role = st.session_state.get('role', '')
    if user_role == 'admin':
        product_id = st.session_state.get('report_product_id', 'default')
        if product_id in st.session_state.reviewer_notes and st.session_state.reviewer_notes[product_id]:
            content += "\n\n## Review History\n\n"
            notes = st.session_state.reviewer_notes[product_id]
            for note in reversed(notes):
                content += f"**{note['timestamp']}** - {note['author']}\n"
                content += f"{note['note']}\n\n"
    
    return content

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
