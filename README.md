# Pharma Pulse - PSUR Generation System

A comprehensive Streamlit web application that automates the generation of PSUR (Periodic Safety Update Reports) in compliance with Indian CDSCO pharmacovigilance standards.

## Features

- **CSV Data Upload & Validation**: Upload and validate 6 required CSV files with real-time schema validation
- **AI-Powered Report Generation**: Uses OpenAI GPT-4o to generate comprehensive PSUR reports
- **Multi-Format Export**: Export reports in both Word (DOCX) and PDF formats
- **User Authentication**: Secure login system with session management
- **PWC Branding**: Professional UI with PWC color scheme and branding
- **Interactive Navigation**: Clickable sidebar navigation for seamless page switching
- **Data Visualization**: Charts and analytics for adverse events and exposure data
- **Comprehensive Logging**: Detailed logging system for debugging and audit trails

## Required CSV Files

1. **Products.csv**: Product information (ProductID, ProductName, INN, DosageForm, Strength)
2. **Authorizations.csv**: Marketing authorizations (AuthorizationID, ProductID, Country, MarketingStatus)
3. **AdverseEvents.csv**: Adverse event reports (AEID, ProductID, ReportedDate, PatientAge, Gender)
4. **RegulatoryActions.csv**: Regulatory actions (ActionID, ProductID, ActionDate, Region, ActionTaken)
5. **ExposureEstimates.csv**: Exposure estimates (ExposureID, ProductID, Region, TimePeriod)
6. **ClinicalStudies.csv**: Clinical study data (StudyID, ProductID, StudyTitle, Status, CompletionDate)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mpriyabrata65/PharmaPulse.git
cd PharmaPulse
```

2. Install dependencies:
```bash
pip install streamlit pandas openai python-docx reportlab matplotlib seaborn markdown anthropic
```

3. Set up environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

4. Run the application:
```bash
streamlit run app.py --server.port 5000
```

## Usage

1. **Login**: Use credentials `admin` / `pwc@123`
2. **Data Upload**: Upload all 6 required CSV files and validate them
3. **Report Generation**: Select a product and date range to generate PSUR reports
4. **Export**: Download generated reports in Word or PDF format

## Architecture

- **Frontend**: Streamlit with custom PWC branding
- **Backend**: Python with pandas for data processing
- **AI Integration**: OpenAI GPT-4o for intelligent report generation
- **Document Generation**: python-docx and reportlab for export functionality
- **Data Validation**: Real-time CSV schema validation with detailed error reporting

## Configuration

The application uses `streamlit/config.toml` for server configuration:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

## File Structure

```
PharmaPulse/
├── app.py                 # Main application entry point
├── psur_app.py           # Main application logic
├── login.py              # Authentication handling
├── backend.py            # Data validation and processing
├── report_generator.py   # AI-powered report generation
├── docx_pdf_exporter.py  # Document export functionality
├── utils.py              # Shared utilities and logging
├── logs/                 # Application logs
├── output/               # Generated reports
└── .streamlit/           # Streamlit configuration
```

## Compliance

This application generates PSUR reports compliant with Indian CDSCO pharmacovigilance standards, including:
- Regulatory requirement adherence
- Structured data presentation
- Professional report formatting
- Audit trail maintenance

## License

This project is developed for pharmaceutical compliance and regulatory reporting purposes.

## Support

For technical support or questions about PSUR generation, please refer to the application documentation or contact the development team.