import pandas as pd
import logging
from typing import Dict, Any, List
import io
from datetime import datetime

logger = logging.getLogger(__name__)

# Define required schemas for each CSV file
REQUIRED_SCHEMAS = {
    'Products.csv': ['ProductID', 'ProductName', 'INN', 'DosageForm', 'Strength'],
    'Authorizations.csv': ['AuthorizationID', 'ProductID', 'Country', 'MarketingStatus', 'AuthorizationDate', 'LicenseNumber'],
    'AdverseEvents.csv': ['AEID', 'ProductID', 'ReportedDate', 'PatientAge', 'Gender', 'EventDescription', 'Outcome'],
    'RegulatoryActions.csv': ['ActionID', 'ProductID', 'ActionDate', 'Region', 'ActionTaken', 'Justification'],
    'ExposureEstimates.csv': ['ExposureID', 'ProductID', 'Region', 'TimePeriod', 'EstimatedPatients', 'EstimationMethod'],
    'ClinicalStudies.csv': ['StudyID', 'ProductID', 'StudyTitle', 'Status', 'CompletionDate']
}

def validate_file_schema(df: pd.DataFrame, required_columns: List[str], file_name: str) -> Dict[str, Any]:
    """
    Validate that a DataFrame has the required columns and basic data quality
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        file_name: Name of the file being validated
    
    Returns:
        Dictionary with validation results
    """
    
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'rows': len(df)
    }
    
    try:
        # Check if DataFrame is empty
        if df.empty:
            validation_result['valid'] = False
            validation_result['errors'].append("File is empty")
            return validation_result
        
        # Check for required columns
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check for extra columns (warning only)
        extra_columns = set(df.columns) - set(required_columns)
        if extra_columns:
            validation_result['warnings'].append(f"Extra columns found: {', '.join(extra_columns)}")
        
        # Check for completely null columns
        null_columns = df.columns[df.isnull().all()].tolist()
        if null_columns:
            validation_result['errors'].append(f"Columns with all null values: {', '.join(null_columns)}")
            validation_result['valid'] = False
        
        # Check for ProductID presence and validity (for files that should have it)
        if 'ProductID' in required_columns:
            if df['ProductID'].isnull().any():
                null_product_ids = df['ProductID'].isnull().sum()
                validation_result['errors'].append(f"Found {null_product_ids} rows with null ProductID")
                validation_result['valid'] = False
            
            # Check for duplicate keys in primary files
            if file_name == 'Products.csv' and 'ProductID' in df.columns:
                if df['ProductID'].duplicated().any():
                    duplicate_count = df['ProductID'].duplicated().sum()
                    validation_result['errors'].append(f"Found {duplicate_count} duplicate ProductIDs")
                    validation_result['valid'] = False
        
        # File-specific validations
        if file_name == 'AdverseEvents.csv':
            # Check for valid age values
            if 'PatientAge' in df.columns:
                invalid_ages = df[(df['PatientAge'] < 0) | (df['PatientAge'] > 120)]['PatientAge'].count()
                if invalid_ages > 0:
                    validation_result['warnings'].append(f"Found {invalid_ages} rows with suspicious age values")
        
        elif file_name == 'ExposureEstimates.csv':
            # Check for valid patient estimates
            if 'EstimatedPatients' in df.columns:
                negative_patients = df[df['EstimatedPatients'] < 0]['EstimatedPatients'].count()
                if negative_patients > 0:
                    validation_result['errors'].append(f"Found {negative_patients} rows with negative patient estimates")
                    validation_result['valid'] = False
        
        logger.info(f"Validation completed for {file_name}: {'Valid' if validation_result['valid'] else 'Invalid'}")
        
    except Exception as e:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Validation error: {str(e)}")
        logger.error(f"Error validating {file_name}: {str(e)}")
    
    return validation_result

def validate_all_files(uploaded_files: Dict) -> Dict[str, Dict[str, Any]]:
    """
    Validate all uploaded files against their required schemas
    
    Args:
        uploaded_files: Dictionary of file names to uploaded file objects
    
    Returns:
        Dictionary of validation results for each file
    """
    
    validation_results = {}
    
    for file_name, uploaded_file in uploaded_files.items():
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Get required schema for this file
            required_columns = REQUIRED_SCHEMAS.get(file_name, [])
            
            # Validate the file
            validation_result = validate_file_schema(df, required_columns, file_name)
            validation_results[file_name] = validation_result
            
        except Exception as e:
            validation_results[file_name] = {
                'valid': False,
                'errors': [f"Error reading file: {str(e)}"],
                'warnings': [],
                'rows': 0
            }
            logger.error(f"Error processing {file_name}: {str(e)}")
    
    return validation_results

def process_validated_files(uploaded_files: Dict) -> Dict[str, pd.DataFrame]:
    """
    Process validated files and return cleaned DataFrames
    
    Args:
        uploaded_files: Dictionary of file names to uploaded file objects
    
    Returns:
        Dictionary of file names to cleaned DataFrames
    """
    
    processed_data = {}
    
    for file_name, uploaded_file in uploaded_files.items():
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Read and clean the data
            df = pd.read_csv(uploaded_file)
            
            # Basic cleaning
            df = clean_dataframe(df, file_name)
            
            processed_data[file_name] = df
            logger.info(f"Processed {file_name}: {len(df)} rows")
            
        except Exception as e:
            logger.error(f"Error processing {file_name}: {str(e)}")
            # Don't add to processed_data if there's an error
    
    return processed_data

def clean_dataframe(df: pd.DataFrame, file_name: str) -> pd.DataFrame:
    """
    Clean a DataFrame by handling common data quality issues
    
    Args:
        df: DataFrame to clean
        file_name: Name of the file for specific cleaning rules
    
    Returns:
        Cleaned DataFrame
    """
    
    # Remove completely empty rows
    df = df.dropna(how='all')
    
    # Strip whitespace from string columns
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace('nan', None)
    
    # File-specific cleaning
    if file_name == 'Products.csv':
        # Ensure ProductID is treated as string
        if 'ProductID' in df.columns:
            df['ProductID'] = df['ProductID'].astype(str)
    
    elif file_name == 'AdverseEvents.csv':
        # Clean age column
        if 'PatientAge' in df.columns:
            df['PatientAge'] = pd.to_numeric(df['PatientAge'], errors='coerce')
        
        # Standardize gender values
        if 'Gender' in df.columns:
            df['Gender'] = df['Gender'].str.upper()
            df['Gender'] = df['Gender'].replace({
                'M': 'Male',
                'F': 'Female',
                'MALE': 'Male',
                'FEMALE': 'Female'
            })
    
    elif file_name == 'ExposureEstimates.csv':
        # Ensure EstimatedPatients is numeric
        if 'EstimatedPatients' in df.columns:
            df['EstimatedPatients'] = pd.to_numeric(df['EstimatedPatients'], errors='coerce')
    
    # Convert date columns to datetime where applicable
    date_columns = [col for col in df.columns if 'Date' in col]
    for col in date_columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
        except:
            logger.warning(f"Could not convert {col} to datetime in {file_name}")
    
    return df

def get_product_data(product_id: str, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Extract all data related to a specific product
    
    Args:
        product_id: Product ID to filter for
        data: Dictionary of all loaded data
    
    Returns:
        Dictionary of filtered DataFrames for the specific product
    """
    
    product_data = {}
    
    try:
        # Get product information
        if 'Products.csv' in data:
            product_info = data['Products.csv'][data['Products.csv']['ProductID'] == product_id]
            product_data['Products.csv'] = product_info
        
        # Get related data for this product
        product_related_files = [
            'Authorizations.csv', 'AdverseEvents.csv', 'RegulatoryActions.csv',
            'ExposureEstimates.csv', 'ClinicalStudies.csv'
        ]
        
        for file_name in product_related_files:
            if file_name in data:
                filtered_df = data[file_name][data[file_name]['ProductID'] == product_id]
                product_data[file_name] = filtered_df
        
        logger.info(f"Extracted data for product {product_id}")
        
    except Exception as e:
        logger.error(f"Error extracting product data for {product_id}: {str(e)}")
    
    return product_data

def validate_product_relationships(data: Dict[str, pd.DataFrame]) -> Dict[str, List[str]]:
    """
    Validate relationships between datasets (e.g., ProductID consistency)
    
    Args:
        data: Dictionary of all loaded data
    
    Returns:
        Dictionary of validation issues found
    """
    
    issues = {}
    
    try:
        if 'Products.csv' not in data:
            issues['general'] = ['Products.csv is required but not provided']
            return issues
        
        # Get all valid ProductIDs
        valid_product_ids = set(data['Products.csv']['ProductID'].dropna().astype(str))
        
        # Check ProductID references in other files
        for file_name, df in data.items():
            if file_name != 'Products.csv' and 'ProductID' in df.columns:
                file_product_ids = set(df['ProductID'].dropna().astype(str))
                invalid_refs = file_product_ids - valid_product_ids
                
                if invalid_refs:
                    if file_name not in issues:
                        issues[file_name] = []
                    issues[file_name].append(
                        f"Found {len(invalid_refs)} invalid ProductID references: {', '.join(list(invalid_refs)[:5])}{'...' if len(invalid_refs) > 5 else ''}"
                    )
        
        logger.info("Product relationship validation completed")
        
    except Exception as e:
        issues['general'] = [f"Error validating relationships: {str(e)}"]
        logger.error(f"Error validating product relationships: {str(e)}")
    
    return issues
