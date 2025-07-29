import os
import logging
from typing import Dict, Any
import pandas as pd
from datetime import datetime
import json

# Gemini AI integration
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Initialize Gemini client
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def generate_psur_report(product_id: str, data: Dict[str, pd.DataFrame]) -> str:
    """
    Generate a comprehensive PSUR report for a specific product using AI
    
    Args:
        product_id: Product ID to generate report for
        data: Dictionary containing all validated data
    
    Returns:
        Generated PSUR report as markdown string
    """
    
    try:
        logger.info(f"Starting PSUR report generation for product: {product_id}")
        
        # Extract product-specific data
        product_data = extract_product_data(product_id, data)
        
        # Prepare data summary for AI
        data_summary = prepare_data_summary(product_data)
        
        # Generate report using AI
        report_content = generate_ai_report(product_id, data_summary, product_data)
        
        logger.info(f"PSUR report generated successfully for product: {product_id}")
        return report_content
        
    except Exception as e:
        logger.error(f"Error generating PSUR report for {product_id}: {str(e)}")
        raise Exception(f"Failed to generate PSUR report: {str(e)}")

def extract_product_data(product_id: str, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Extract all data related to a specific product"""
    
    product_data = {}
    
    # Get product information
    if 'Products.csv' in data:
        product_info = data['Products.csv'][data['Products.csv']['ProductID'] == product_id]
        product_data['Products'] = product_info
    
    # Get related data for this product
    related_files = {
        'Authorizations': 'Authorizations.csv',
        'AdverseEvents': 'AdverseEvents.csv', 
        'RegulatoryActions': 'RegulatoryActions.csv',
        'ExposureEstimates': 'ExposureEstimates.csv',
        'ClinicalStudies': 'ClinicalStudies.csv'
    }
    
    for key, file_name in related_files.items():
        if file_name in data:
            filtered_df = data[file_name][data[file_name]['ProductID'] == product_id]
            product_data[key] = filtered_df
    
    return product_data

def prepare_data_summary(product_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Prepare a summary of the data for AI processing"""
    
    summary = {}
    
    try:
        # Debug logging
        logger.info(f"Preparing data summary for product data keys: {list(product_data.keys())}")
        for key, df in product_data.items():
            logger.info(f"Data for {key}: {len(df) if df is not None else 0} rows")
        # Product information
        if 'Products' in product_data and not product_data['Products'].empty:
            product_info = product_data['Products'].iloc[0]
            summary['product'] = {
                'id': product_info.get('ProductID', 'N/A'),
                'name': product_info.get('ProductName', 'N/A'),
                'inn': product_info.get('INN', 'N/A'),
                'dosage_form': product_info.get('DosageForm', 'N/A'),
                'strength': product_info.get('Strength', 'N/A')
            }
        else:
            summary['product'] = {'id': 'N/A', 'name': 'N/A', 'inn': 'N/A', 'dosage_form': 'N/A', 'strength': 'N/A'}
        
        # Authorization summary
        if 'Authorizations' in product_data and not product_data['Authorizations'].empty:
            auth_df = product_data['Authorizations']
            summary['authorizations'] = {
                'total_countries': len(auth_df['Country'].unique()),
                'countries': auth_df['Country'].unique().tolist(),
                'marketing_statuses': auth_df['MarketingStatus'].value_counts().to_dict(),
                'latest_authorization': auth_df['AuthorizationDate'].max() if 'AuthorizationDate' in auth_df.columns else 'N/A'
            }
        else:
            summary['authorizations'] = {'total_countries': 0, 'countries': [], 'marketing_statuses': {}, 'latest_authorization': 'N/A'}
        
        # Adverse events summary
        if 'AdverseEvents' in product_data and not product_data['AdverseEvents'].empty:
            ae_df = product_data['AdverseEvents']
            summary['adverse_events'] = {
                'total_events': len(ae_df),
                'outcomes': ae_df['Outcome'].value_counts().to_dict(),
                'age_distribution': {
                    'mean_age': ae_df['PatientAge'].mean() if 'PatientAge' in ae_df.columns else 0,
                    'age_ranges': get_age_distribution(ae_df)
                },
                'gender_distribution': ae_df['Gender'].value_counts().to_dict() if 'Gender' in ae_df.columns else {},
                'recent_events': len(ae_df[ae_df['ReportedDate'] >= '2023-01-01']) if 'ReportedDate' in ae_df.columns else 0
            }
        else:
            summary['adverse_events'] = {'total_events': 0, 'outcomes': {}, 'age_distribution': {}, 'gender_distribution': {}, 'recent_events': 0}
        
        # Regulatory actions summary
        if 'RegulatoryActions' in product_data and not product_data['RegulatoryActions'].empty:
            reg_df = product_data['RegulatoryActions']
            summary['regulatory_actions'] = {
                'total_actions': len(reg_df),
                'action_types': reg_df['ActionTaken'].value_counts().to_dict(),
                'regions': reg_df['Region'].unique().tolist(),
                'recent_actions': len(reg_df[reg_df['ActionDate'] >= '2023-01-01']) if 'ActionDate' in reg_df.columns else 0
            }
        else:
            summary['regulatory_actions'] = {'total_actions': 0, 'action_types': {}, 'regions': [], 'recent_actions': 0}
        
        # Exposure estimates summary
        if 'ExposureEstimates' in product_data and not product_data['ExposureEstimates'].empty:
            exp_df = product_data['ExposureEstimates']
            summary['exposure'] = {
                'total_estimated_patients': exp_df['EstimatedPatients'].sum() if 'EstimatedPatients' in exp_df.columns else 0,
                'regions': exp_df['Region'].unique().tolist(),
                'estimation_methods': exp_df['EstimationMethod'].value_counts().to_dict() if 'EstimationMethod' in exp_df.columns else {}
            }
        else:
            summary['exposure'] = {'total_estimated_patients': 0, 'regions': [], 'estimation_methods': {}}
        
        # Clinical studies summary
        if 'ClinicalStudies' in product_data and not product_data['ClinicalStudies'].empty:
            studies_df = product_data['ClinicalStudies']
            summary['clinical_studies'] = {
                'total_studies': len(studies_df),
                'study_statuses': studies_df['Status'].value_counts().to_dict(),
                'completed_studies': len(studies_df[studies_df['Status'] == 'Completed']) if 'Status' in studies_df.columns else 0
            }
        else:
            summary['clinical_studies'] = {'total_studies': 0, 'study_statuses': {}, 'completed_studies': 0}
        
    except Exception as e:
        logger.error(f"Error preparing data summary: {str(e)}")
        raise
    
    return summary

def get_age_distribution(ae_df: pd.DataFrame) -> Dict[str, int]:
    """Get age distribution for adverse events"""
    
    if 'PatientAge' not in ae_df.columns:
        return {}
    
    age_ranges = {
        '0-17': 0,
        '18-64': 0,
        '65+': 0,
        'Unknown': 0
    }
    
    for age in ae_df['PatientAge'].dropna():
        if age < 18:
            age_ranges['0-17'] += 1
        elif age <= 64:
            age_ranges['18-64'] += 1
        else:
            age_ranges['65+'] += 1
    
    age_ranges['Unknown'] = ae_df['PatientAge'].isna().sum()
    
    return age_ranges

def generate_ai_report(product_id: str, data_summary: Dict[str, Any], product_data: Dict[str, pd.DataFrame]) -> str:
    """Generate the actual PSUR report using Gemini AI"""
    
    try:
        # Prepare the prompt for AI
        prompt = create_psur_prompt(product_id, data_summary, product_data)
        
        # System instruction for Gemini
        system_instruction = """You are a specialized PSUR (Periodic Safety Update Report) generation assistant with expertise in Indian CDSCO pharmacovigilance standards and ICH E2C(R2) guidelines. 

Generate comprehensive, professional PSUR reports that are compliant with regulatory requirements. Use proper medical terminology, maintain professional tone, and ensure all sections are thoroughly documented.

Format the output in clean markdown with proper headers, tables, and formatting. Include all 12 ICH E2C(R2) sections as specified."""
        
        # Call Gemini API
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=4000,
                temperature=0.3
            )
        )
        
        report_content = response.text
        
        # Post-process the report
        final_report = post_process_report(report_content or "", data_summary)
        
        return final_report
        
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        # For any API errors, use enhanced fallback report with actual data
        logger.info("Gemini API error, using enhanced fallback report with actual data")
        return generate_enhanced_fallback_report(product_id, data_summary, product_data)

def create_psur_prompt(product_id: str, data_summary: Dict[str, Any], product_data: Dict[str, pd.DataFrame]) -> str:
    """Create a detailed prompt for AI-powered PSUR generation"""
    
    # Convert data summary to JSON for better AI processing
    data_json = json.dumps(data_summary, indent=2, default=str)
    
    prompt = f"""
Generate a comprehensive PSUR (Periodic Safety Update Report) for Product ID: {product_id} following Indian CDSCO pharmacovigilance standards and ICH E2C(R2) guidelines.

**Data Summary:**
```json
{data_json}
```

**Required PSUR Structure (ICH E2C(R2) - 12 Sections):**

1. **Title Page**
   - Product name, INN, dosage form, strength
   - PSUR period covered
   - Company information

2. **Executive Summary**
   - Key safety findings
   - Regulatory actions taken
   - Overall benefit-risk assessment

3. **Introduction**
   - Product description and therapeutic indication
   - Marketing authorization status

4. **Worldwide Marketing Authorization Status**
   - Countries where authorized
   - Marketing statuses by region

5. **Update on Actions Taken for Safety Reasons**
   - Regulatory actions during the reporting period
   - Safety-related changes to product information

6. **Changes to Reference Safety Information**
   - Updates to safety profile
   - New contraindications or warnings

7. **Estimated Patient Exposure**
   - Patient exposure data by region
   - Estimation methodology

8. **Presentation of Individual Case Histories**
   - Adverse event case summaries
   - Serious adverse events analysis

9. **Studies**
   - Clinical studies relevant to safety
   - Post-marketing surveillance studies

10. **Other Information**
    - Literature review
    - Additional safety data

11. **Overall Safety Evaluation**
    - Benefit-risk analysis
    - Emerging safety signals

12. **Conclusion and Appendices**
    - Summary of findings
    - Supporting documentation

**Instructions:**
- Use professional medical terminology
- Include data tables where appropriate
- Mark sections as "Data not available" if no data exists
- Highlight adverse event trends if ≥3 events reported
- Format dates as DD-MMM-YYYY
- Ensure CDSCO compliance throughout
- Provide comprehensive analysis based on available data

Generate the complete PSUR report in markdown format with proper headers and professional formatting.
"""
    
    return prompt

def post_process_report(report_content: str, data_summary: Dict[str, Any]) -> str:
    """Post-process the generated report for consistency and formatting"""
    
    try:
        # Add timestamp
        timestamp = datetime.now().strftime("%d-%b-%Y")
        
        # Add header with product information
        product_info = data_summary.get('product', {})
        product_name = product_info.get('name', 'Unknown Product')
        product_id = product_info.get('id', 'Unknown ID')
        
        header = f"""
# PSUR Report - {product_name} (ID: {product_id})
**Report Generated:** {timestamp}
**Compliance:** Indian CDSCO Standards & ICH E2C(R2)

---

"""
        
        # Combine header with report content
        final_report = header + report_content
        
        # Add footer
        footer = f"""

---

**Report Generation Information:**
- Generated by: Pharma Pulse System
- Date: {timestamp}
- Standards: CDSCO & ICH E2C(R2)
- AI Model: Google Gemini 2.5 Flash

*This report has been automatically generated based on the provided data and should be reviewed by qualified pharmacovigilance professionals before submission.*
"""
        
        final_report += footer
        
        return final_report
        
    except Exception as e:
        logger.error(f"Error post-processing report: {str(e)}")
        return report_content

def generate_fallback_report(product_id: str, data_summary: Dict[str, Any], product_data: Dict[str, pd.DataFrame]) -> str:
    """Generate a basic template-based report if AI fails"""
    
    try:
        product_info = data_summary.get('product', {})
        product_name = product_info.get('name', 'Unknown Product')
        timestamp = datetime.now().strftime("%d-%b-%Y")
        
        fallback_report = f"""
# PSUR Report - {product_name} (ID: {product_id})
**Report Generated:** {timestamp}
**Compliance:** Indian CDSCO Standards & ICH E2C(R2)

---

## Executive Summary

This PSUR report has been generated for {product_name} (Product ID: {product_id}) based on available data.

**Key Statistics:**
- Total Adverse Events: {data_summary.get('adverse_events', {}).get('total_events', 0)}
- Authorized Countries: {data_summary.get('authorizations', {}).get('total_countries', 0)}
- Estimated Patient Exposure: {data_summary.get('exposure', {}).get('total_estimated_patients', 0)}
- Clinical Studies: {data_summary.get('clinical_studies', {}).get('total_studies', 0)}

## 1. Title Page

**Product Name:** {product_name}
**Product ID:** {product_id}
**INN:** {product_info.get('inn', 'N/A')}
**Dosage Form:** {product_info.get('dosage_form', 'N/A')}
**Strength:** {product_info.get('strength', 'N/A')}

## 2. Executive Summary

Based on the available data, this report summarizes the safety profile of {product_name}.

## 3. Introduction

Product description and indication information would be populated here based on complete product data.

## 4. Worldwide Marketing Authorization Status

**Countries with Authorization:** {len(data_summary.get('authorizations', {}).get('countries', []))}

## 5. Update on Actions Taken for Safety Reasons

**Total Regulatory Actions:** {data_summary.get('regulatory_actions', {}).get('total_actions', 0)}

## 6. Changes to Reference Safety Information

Data not available in current dataset.

## 7. Estimated Patient Exposure

**Total Estimated Patients:** {data_summary.get('exposure', {}).get('total_estimated_patients', 0)}

## 8. Presentation of Individual Case Histories

**Total Adverse Events Reported:** {data_summary.get('adverse_events', {}).get('total_events', 0)}

## 9. Studies

**Total Studies:** {data_summary.get('clinical_studies', {}).get('total_studies', 0)}
**Completed Studies:** {data_summary.get('clinical_studies', {}).get('completed_studies', 0)}

## 10. Other Information

Additional safety information would be included based on literature review and other sources.

## 11. Overall Safety Evaluation

The benefit-risk assessment is based on the available data and requires clinical evaluation.

## 12. Conclusion and Appendices

This report provides a summary of available safety data for {product_name}.

---

**Note:** This is a fallback report generated due to AI service unavailability. For complete PSUR generation, please ensure AI services are properly configured.

**Report Generation Information:**
- Generated by: Pharma Pulse System (Fallback Mode)
- Date: {timestamp}
- Standards: CDSCO & ICH E2C(R2)
"""
        
        logger.info(f"Fallback report generated for product: {product_id}")
        return fallback_report
        
    except Exception as e:
        logger.error(f"Error generating fallback report: {str(e)}")
        return f"Error generating report for product {product_id}. Please check the logs for details."

def generate_enhanced_fallback_report(product_id: str, data_summary: Dict[str, Any], product_data: Dict[str, pd.DataFrame]) -> str:
    """Generate an enhanced fallback report using actual data when AI service is unavailable"""
    
    try:
        product_info = data_summary.get('product', {})
        product_name = product_info.get('name', 'Unknown Product')
        timestamp = datetime.now().strftime("%d-%b-%Y")
        
        # Get actual data statistics
        ae_data = data_summary.get('adverse_events', {})
        auth_data = data_summary.get('authorizations', {})
        exposure_data = data_summary.get('exposure', {})
        studies_data = data_summary.get('clinical_studies', {})
        reg_actions_data = data_summary.get('regulatory_actions', {})
        
        enhanced_report = f"""
# PSUR Report - {product_name} (ID: {product_id})
**Report Generated:** {timestamp}
**Compliance:** Indian CDSCO Standards & ICH E2C(R2)

---

## Executive Summary

This PSUR report has been generated for **{product_name}** (Product ID: {product_id}) based on actual uploaded data. This report uses your actual uploaded data. AI-enhanced analysis will be available once Gemini service is restored.

**Key Safety Statistics:**
- **Total Adverse Events:** {ae_data.get('total_events', 0)}
- **Authorized Countries:** {auth_data.get('total_countries', 0)}
- **Estimated Patient Exposure:** {exposure_data.get('total_estimated_patients', 0):,}
- **Clinical Studies:** {studies_data.get('total_studies', 0)}
- **Regulatory Actions:** {reg_actions_data.get('total_actions', 0)}

## 1. Title Page

**Product Name:** {product_name}
**Product ID:** {product_id}
**INN:** {product_info.get('inn', 'N/A')}
**Dosage Form:** {product_info.get('dosage_form', 'N/A')}
**Strength:** {product_info.get('strength', 'N/A')}
**PSUR Period:** {timestamp}
**Reporting Company:** Pharma Pulse System

## 2. Executive Summary

This report summarizes the safety profile of {product_name} based on data from {auth_data.get('total_countries', 0)} countries where the product is authorized.

**Key Findings:**
- Total adverse events reported: {ae_data.get('total_events', 0)}
- Patient exposure estimated at: {exposure_data.get('total_estimated_patients', 0):,} patients
- Regulatory actions taken: {reg_actions_data.get('total_actions', 0)}

## 3. Introduction

**Product:** {product_name} ({product_info.get('inn', 'N/A')})
**Dosage Form:** {product_info.get('dosage_form', 'N/A')}
**Strength:** {product_info.get('strength', 'N/A')}

The product is currently authorized in {auth_data.get('total_countries', 0)} countries worldwide.

## 4. Worldwide Marketing Authorization Status

**Total Authorized Countries:** {auth_data.get('total_countries', 0)}

**Countries with Authorization:**"""

        # Add country list if available
        if auth_data.get('countries'):
            for country in auth_data.get('countries', []):
                enhanced_report += f"\n- {country}"
        else:
            enhanced_report += "\n- Data not available"

        enhanced_report += f"""

**Marketing Status Distribution:**"""

        # Add marketing status distribution
        if auth_data.get('marketing_statuses'):
            for status, count in auth_data.get('marketing_statuses', {}).items():
                enhanced_report += f"\n- {status}: {count}"
        else:
            enhanced_report += "\n- Data not available"

        enhanced_report += f"""

## 5. Update on Actions Taken for Safety Reasons

**Total Regulatory Actions:** {reg_actions_data.get('total_actions', 0)}

**Action Types:**"""

        # Add action types if available
        if reg_actions_data.get('action_types'):
            for action, count in reg_actions_data.get('action_types', {}).items():
                enhanced_report += f"\n- {action}: {count} action(s)"
        else:
            enhanced_report += "\n- No regulatory actions reported"

        enhanced_report += f"""

## 6. Changes to Reference Safety Information

Based on the adverse events data, {"no significant safety signals were identified" if ae_data.get('total_events', 0) < 3 else "adverse event patterns require clinical evaluation"}.

## 7. Estimated Patient Exposure

**Total Estimated Patients:** {exposure_data.get('total_estimated_patients', 0):,}

**Regional Distribution:**"""

        # Add regional exposure if available
        if exposure_data.get('regions'):
            for region in exposure_data.get('regions', []):
                enhanced_report += f"\n- {region}"
        else:
            enhanced_report += "\n- Regional data not available"

        enhanced_report += f"""

**Estimation Methods:**"""

        # Add estimation methods if available  
        if exposure_data.get('estimation_methods'):
            for method, count in exposure_data.get('estimation_methods', {}).items():
                enhanced_report += f"\n- {method}: {count} estimate(s)"
        else:
            enhanced_report += "\n- Estimation methodology not specified"

        enhanced_report += f"""

## 8. Presentation of Individual Case Histories

**Total Adverse Events:** {ae_data.get('total_events', 0)}

**Outcome Distribution:**"""

        # Add outcome distribution
        if ae_data.get('outcomes'):
            for outcome, count in ae_data.get('outcomes', {}).items():
                enhanced_report += f"\n- {outcome}: {count} case(s)"
        else:
            enhanced_report += "\n- No adverse events reported"

        enhanced_report += f"""

**Age Distribution:**"""

        # Add age distribution
        if ae_data.get('age_distribution', {}).get('age_ranges'):
            for age_range, count in ae_data.get('age_distribution', {}).get('age_ranges', {}).items():
                enhanced_report += f"\n- {age_range}: {count} case(s)"
        else:
            enhanced_report += "\n- Age distribution data not available"

        enhanced_report += f"""

**Gender Distribution:**"""

        # Add gender distribution
        if ae_data.get('gender_distribution'):
            for gender, count in ae_data.get('gender_distribution', {}).items():
                enhanced_report += f"\n- {gender}: {count} case(s)"
        else:
            enhanced_report += "\n- Gender distribution data not available"

        enhanced_report += f"""

## 9. Studies

**Total Clinical Studies:** {studies_data.get('total_studies', 0)}
**Completed Studies:** {studies_data.get('completed_studies', 0)}

**Study Status Distribution:**"""

        # Add study statuses
        if studies_data.get('study_statuses'):
            for status, count in studies_data.get('study_statuses', {}).items():
                enhanced_report += f"\n- {status}: {count} study/studies"
        else:
            enhanced_report += "\n- No clinical studies data available"

        enhanced_report += f"""

## 10. Other Information

**Recent Events (2023+):** {ae_data.get('recent_events', 0)} adverse events
**Recent Actions (2023+):** {reg_actions_data.get('recent_actions', 0)} regulatory actions

Additional safety information from literature review and post-marketing surveillance would be included in a complete assessment.

## 11. Overall Safety Evaluation

Based on the available data:

- **Adverse Event Rate:** {ae_data.get('total_events', 0)} events reported from {exposure_data.get('total_estimated_patients', 0):,} exposed patients
- **Regulatory Oversight:** {reg_actions_data.get('total_actions', 0)} regulatory actions taken
- **Study Evidence:** {studies_data.get('completed_studies', 0)} completed clinical studies available

{'**Assessment:** The safety profile appears acceptable based on current data.' if ae_data.get('total_events', 0) < 10 else '**Assessment:** Detailed clinical review recommended due to adverse event volume.'}

## 12. Conclusion and Appendices

**Summary:**
- Product is authorized in {auth_data.get('total_countries', 0)} countries
- {ae_data.get('total_events', 0)} adverse events reported from {exposure_data.get('total_estimated_patients', 0):,} patients
- {reg_actions_data.get('total_actions', 0)} regulatory actions implemented
- {studies_data.get('total_studies', 0)} clinical studies on record

**Recommendation:** Continue monitoring safety profile with regular PSUR updates as per regulatory requirements.

---

**Report Generation Information:**
- Generated by: Pharma Pulse System (Enhanced Data Mode)
- Date: {timestamp}
- Standards: CDSCO & ICH E2C(R2)
- Data Source: User-uploaded CSV files (actual data)

*Note: This report uses your actual uploaded data. AI-enhanced analysis will be available once OpenAI service quotas are restored.*
"""
        
        logger.info(f"Enhanced fallback report generated for product: {product_id}")
        return enhanced_report
        
    except Exception as e:
        logger.error(f"Error generating enhanced fallback report: {str(e)}")
        return generate_fallback_report(product_id, data_summary, product_data)