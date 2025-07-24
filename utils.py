import logging
import os
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Any, List
import seaborn as sns

def setup_logging():
    """Setup logging configuration with rotating logs"""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create log filename with current date
    log_filename = f"log_{datetime.now().strftime('%Y%m%d')}.txt"
    log_path = logs_dir / log_filename
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Pharma Pulse application started")
    logger.info(f"Logging to: {log_path}")

def create_adverse_events_chart(ae_data: pd.DataFrame, product_id: str) -> str:
    """
    Create adverse events outcome chart
    
    Args:
        ae_data: Adverse events DataFrame
        product_id: Product ID for chart title
    
    Returns:
        Path to saved chart image
    """
    
    try:
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Outcome distribution pie chart
        if 'Outcome' in ae_data.columns and not ae_data['Outcome'].empty:
            outcome_counts = ae_data['Outcome'].value_counts()
            
            ax1.pie(outcome_counts.values, labels=outcome_counts.index, autopct='%1.1f%%', startangle=90)
            ax1.set_title(f'Adverse Events Outcomes\nProduct: {product_id}')
        else:
            ax1.text(0.5, 0.5, 'No outcome data available', ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title(f'Adverse Events Outcomes\nProduct: {product_id}')
        
        # Age distribution bar chart
        if 'PatientAge' in ae_data.columns and not ae_data['PatientAge'].empty:
            # Create age groups
            age_bins = [0, 18, 30, 50, 65, 100]
            age_labels = ['0-17', '18-29', '30-49', '50-64', '65+']
            ae_data['AgeGroup'] = pd.cut(ae_data['PatientAge'], bins=age_bins, labels=age_labels, right=False)
            
            age_counts = ae_data['AgeGroup'].value_counts().sort_index()
            
            bars = ax2.bar(range(len(age_counts)), age_counts.values)
            ax2.set_xlabel('Age Group')
            ax2.set_ylabel('Number of Events')
            ax2.set_title('Adverse Events by Age Group')
            ax2.set_xticks(range(len(age_counts)))
            ax2.set_xticklabels(age_counts.index, rotation=45)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
        else:
            ax2.text(0.5, 0.5, 'No age data available', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Adverse Events by Age Group')
        
        plt.tight_layout()
        
        # Save chart
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_filename = f"AE_Chart_{product_id}_{timestamp}.png"
        chart_path = output_dir / chart_filename
        
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.getLogger(__name__).info(f"Adverse events chart created: {chart_path}")
        return str(chart_path)
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error creating adverse events chart: {str(e)}")
        return ""

def create_exposure_chart(exposure_data: pd.DataFrame, product_id: str) -> str:
    """
    Create patient exposure chart by region
    
    Args:
        exposure_data: Exposure estimates DataFrame
        product_id: Product ID for chart title
    
    Returns:
        Path to saved chart image
    """
    
    try:
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('default')
        sns.set_palette("viridis")
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if 'Region' in exposure_data.columns and 'EstimatedPatients' in exposure_data.columns:
            # Group by region and sum estimated patients
            regional_exposure = exposure_data.groupby('Region')['EstimatedPatients'].sum().sort_values(ascending=True)
            
            if not regional_exposure.empty:
                bars = ax.barh(range(len(regional_exposure)), regional_exposure.values)
                ax.set_xlabel('Estimated Patients')
                ax.set_ylabel('Region')
                ax.set_title(f'Patient Exposure by Region\nProduct: {product_id}')
                ax.set_yticks(range(len(regional_exposure)))
                ax.set_yticklabels(regional_exposure.index)
                
                # Add value labels on bars
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax.text(width, bar.get_y() + bar.get_height()/2.,
                           f'{int(width):,}', ha='left', va='center', fontweight='bold')
                
                # Format x-axis to show thousands
                ax.ticklabel_format(style='plain', axis='x')
                
            else:
                ax.text(0.5, 0.5, 'No exposure data available', ha='center', va='center', transform=ax.transAxes)
        else:
            ax.text(0.5, 0.5, 'No exposure data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f'Patient Exposure by Region\nProduct: {product_id}')
        
        plt.tight_layout()
        
        # Save chart
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_filename = f"Exposure_Chart_{product_id}_{timestamp}.png"
        chart_path = output_dir / chart_filename
        
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.getLogger(__name__).info(f"Exposure chart created: {chart_path}")
        return str(chart_path)
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error creating exposure chart: {str(e)}")
        return ""

def create_regulatory_actions_timeline(reg_data: pd.DataFrame, product_id: str) -> str:
    """
    Create regulatory actions timeline chart
    
    Args:
        reg_data: Regulatory actions DataFrame
        product_id: Product ID for chart title
    
    Returns:
        Path to saved chart image
    """
    
    try:
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('default')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if 'ActionDate' in reg_data.columns and 'ActionTaken' in reg_data.columns and not reg_data.empty:
            # Convert date column
            reg_data['ActionDate'] = pd.to_datetime(reg_data['ActionDate'], errors='coerce')
            reg_data = reg_data.dropna(subset=['ActionDate'])
            
            if not reg_data.empty:
                # Group by month and count actions
                reg_data['YearMonth'] = reg_data['ActionDate'].dt.to_period('M')
                monthly_actions = reg_data.groupby('YearMonth').size()
                
                ax.plot(monthly_actions.index.astype(str), monthly_actions.values, marker='o', linewidth=2, markersize=6)
                ax.set_xlabel('Month')
                ax.set_ylabel('Number of Actions')
                ax.set_title(f'Regulatory Actions Timeline\nProduct: {product_id}')
                ax.grid(True, alpha=0.3)
                
                # Rotate x-axis labels for better readability
                plt.xticks(rotation=45)
                
                # Add value labels on points
                for i, v in enumerate(monthly_actions.values):
                    ax.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')
            else:
                ax.text(0.5, 0.5, 'No valid regulatory actions data', ha='center', va='center', transform=ax.transAxes)
        else:
            ax.text(0.5, 0.5, 'No regulatory actions data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f'Regulatory Actions Timeline\nProduct: {product_id}')
        
        plt.tight_layout()
        
        # Save chart
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_filename = f"RegActions_Chart_{product_id}_{timestamp}.png"
        chart_path = output_dir / chart_filename
        
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.getLogger(__name__).info(f"Regulatory actions chart created: {chart_path}")
        return str(chart_path)
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error creating regulatory actions chart: {str(e)}")
        return ""

def validate_environment():
    """Validate that all required environment variables and dependencies are available"""
    
    logger = logging.getLogger(__name__)
    issues = []
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("OPENAI_API_KEY environment variable not set")
    
    # Check if output directory is writable
    try:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        test_file = output_dir / "test_write.txt"
        test_file.write_text("test")
        test_file.unlink()
    except Exception as e:
        issues.append(f"Output directory not writable: {str(e)}")
    
    # Check if logs directory is writable
    try:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        test_file = logs_dir / "test_write.txt"
        test_file.write_text("test")
        test_file.unlink()
    except Exception as e:
        issues.append(f"Logs directory not writable: {str(e)}")
    
    if issues:
        for issue in issues:
            logger.warning(f"Environment issue: {issue}")
        return False, issues
    else:
        logger.info("Environment validation passed")
        return True, []

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amounts for display"""
    
    if pd.isna(amount) or amount == 0:
        return "N/A"
    
    if amount >= 1_000_000:
        return f"{currency} {amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"{currency} {amount/1_000:.1f}K"
    else:
        return f"{currency} {amount:.0f}"

def format_large_numbers(number: int) -> str:
    """Format large numbers for display"""
    
    if pd.isna(number) or number == 0:
        return "0"
    
    if number >= 1_000_000:
        return f"{number/1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number/1_000:.1f}K"
    else:
        return f"{number:,}"

def clean_temp_files():
    """Clean temporary files from the system"""
    
    logger = logging.getLogger(__name__)
    
    try:
        # Clean matplotlib cache
        plt.close('all')
        
        # Remove old temporary files
        temp_patterns = ["*.tmp", "*.temp"]
        output_dir = Path("output")
        
        if output_dir.exists():
            for pattern in temp_patterns:
                for temp_file in output_dir.glob(pattern):
                    temp_file.unlink()
                    logger.info(f"Removed temporary file: {temp_file}")
        
    except Exception as e:
        logger.error(f"Error cleaning temporary files: {str(e)}")

def get_system_stats() -> Dict[str, Any]:
    """Get system statistics for monitoring"""
    
    try:
        output_dir = Path("output")
        logs_dir = Path("logs")
        
        stats = {
            "output_files": len(list(output_dir.glob("*"))) if output_dir.exists() else 0,
            "log_files": len(list(logs_dir.glob("*.txt"))) if logs_dir.exists() else 0,
            "total_disk_usage_mb": get_directory_size(output_dir) + get_directory_size(logs_dir),
            "last_activity": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return stats
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error getting system stats: {str(e)}")
        return {}

def get_directory_size(directory: Path) -> float:
    """Get directory size in MB"""
    
    try:
        if not directory.exists():
            return 0
        
        total_size = sum(f.stat().st_size for f in directory.glob('**/*') if f.is_file())
        return total_size / (1024 * 1024)  # Convert to MB
        
    except Exception:
        return 0

def create_dashboard_summary(data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Create a summary for dashboard display"""
    
    summary = {
        "total_products": 0,
        "total_adverse_events": 0,
        "total_authorizations": 0,
        "total_exposure": 0,
        "total_studies": 0,
        "total_reg_actions": 0
    }
    
    try:
        # Count products
        if 'Products.csv' in data:
            summary["total_products"] = len(data['Products.csv'])
        
        # Count adverse events
        if 'AdverseEvents.csv' in data:
            summary["total_adverse_events"] = len(data['AdverseEvents.csv'])
        
        # Count authorizations
        if 'Authorizations.csv' in data:
            summary["total_authorizations"] = len(data['Authorizations.csv'])
        
        # Sum exposure
        if 'ExposureEstimates.csv' in data and 'EstimatedPatients' in data['ExposureEstimates.csv'].columns:
            summary["total_exposure"] = int(data['ExposureEstimates.csv']['EstimatedPatients'].sum())
        
        # Count studies
        if 'ClinicalStudies.csv' in data:
            summary["total_studies"] = len(data['ClinicalStudies.csv'])
        
        # Count regulatory actions
        if 'RegulatoryActions.csv' in data:
            summary["total_reg_actions"] = len(data['RegulatoryActions.csv'])
        
    except Exception as e:
        logging.getLogger(__name__).error(f"Error creating dashboard summary: {str(e)}")
    
    return summary
