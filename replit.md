# Pharma Pulse - PSUR Generation System

## Overview

Pharma Pulse is a Streamlit web application that automates the generation of PSUR (Periodic Safety Update Reports) in compliance with Indian CDSCO pharmacovigilance standards. The application provides a complete workflow from data upload and validation to AI-powered report generation with export capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for rapid development of data-centric applications
- **Multi-page Navigation**: Session-based page routing with sidebar navigation
- **UI Design**: PwC branding with custom CSS styling using company colors (#E03C31 red, #FFB612 yellow)
- **Authentication Flow**: Simple form-based login with hardcoded credentials stored in session state

### Backend Architecture
- **Modular Design**: Separated into distinct modules for maintainability:
  - `app.py` - Main application entry point and routing
  - `login.py` - Authentication handling
  - `psur_app.py` - Main application logic after login
  - `backend.py` - Data validation and processing
  - `report_generator.py` - AI-powered report generation
  - `docx_pdf_exporter.py` - Document export functionality
  - `utils.py` - Shared utilities and logging

### Data Processing Pipeline
- **CSV Validation**: Schema validation for 6 required CSV files with predefined column requirements
- **Data Quality Checks**: Missing columns detection, empty file validation, and data integrity checks
- **Product-specific Filtering**: Extraction of product-specific data across all uploaded files

## Key Components

### Authentication System
- **Implementation**: Session-based authentication using Streamlit session state
- **Credentials**: Hardcoded admin/pwc@123 for demonstration purposes
- **Session Management**: Maintains login state and handles logout functionality

### Data Upload and Validation
- **Required Files**: 6 CSV files with specific schemas:
  - Products.csv (ProductID, ProductName, INN, DosageForm, Strength)
  - Authorizations.csv (AuthorizationID, ProductID, Country, MarketingStatus, etc.)
  - AdverseEvents.csv (AEID, ProductID, ReportedDate, PatientAge, Gender, etc.)
  - RegulatoryActions.csv (ActionID, ProductID, ActionDate, Region, ActionTaken, etc.)
  - ExposureEstimates.csv (ExposureID, ProductID, Region, TimePeriod, etc.)
  - ClinicalStudies.csv (StudyID, ProductID, StudyTitle, Status, CompletionDate)
- **Validation Engine**: Real-time schema validation with detailed error reporting

### AI Report Generation
- **AI Provider**: OpenAI GPT-4o integration for intelligent report generation
- **Report Structure**: CDSCO-compliant PSUR format with regulatory standards
- **Data Integration**: Combines validated data from all sources for comprehensive analysis

### Document Export System
- **Multiple Formats**: DOCX and PDF export capabilities
- **Document Generation**: Uses python-docx and reportlab libraries
- **File Management**: Timestamped file naming and organized output directory structure

### Visualization and Analytics
- **Charts**: Adverse events outcome charts using matplotlib and seaborn
- **Data Insights**: Statistical analysis and trend visualization for regulatory reporting

## Data Flow

1. **Authentication**: User logs in through form-based authentication
2. **Data Upload**: Upload 6 required CSV files through Streamlit file uploader
3. **Validation**: Each file validated against predefined schemas with error reporting
4. **Storage**: Validated data stored in session state for processing
5. **Report Generation**: AI processes product-specific data to generate PSUR reports
6. **Export**: Generated reports exported to DOCX/PDF formats with download capability

## External Dependencies

### Core Libraries
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **openai**: AI-powered report generation using GPT-4o
- **python-docx**: Microsoft Word document generation
- **reportlab**: PDF document generation
- **matplotlib/seaborn**: Data visualization and chart generation
- **markdown**: Markdown processing for report formatting

### Development Tools
- **logging**: Comprehensive application logging with file rotation
- **pathlib**: Modern file path handling
- **datetime**: Timestamp generation for files and logs

## Deployment Strategy

### File Structure
- **Modular Architecture**: Clear separation of concerns across multiple Python modules
- **Output Management**: Dedicated output directory for generated reports and charts
- **Logging System**: Centralized logging with daily log rotation in logs directory

### Environment Configuration
- **API Keys**: OpenAI API key managed through environment variables
- **File Paths**: Relative path handling for cross-platform compatibility
- **Resource Management**: Automatic directory creation for outputs and logs

### Session Management
- **State Persistence**: Streamlit session state for user authentication and data storage
- **Memory Management**: Efficient DataFrame storage and processing
- **User Experience**: Seamless navigation between pages with preserved state

### Error Handling
- **Comprehensive Logging**: Detailed error tracking and debugging information
- **User Feedback**: Clear error messages and validation feedback
- **Graceful Degradation**: Robust error handling prevents application crashes