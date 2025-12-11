"""Utility functions for Pharmyrus v4.0"""
import re
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def extract_country_code(patent_number: str) -> str:
    """
    Extract country code from patent number
    
    Examples:
        "BR112012008823B8" -> "BR"
        "US9376391B2" -> "US"
        "EP2496562B1" -> "EP"
    """
    # Common patterns: BR/US/EP/CN/JP/etc at start
    match = re.match(r'^([A-Z]{2})', patent_number.upper())
    if match:
        return match.group(1)
    return "Unknown"

def clean_patent_number(patent_number: str) -> str:
    """
    Clean patent number (remove spaces, normalize)
    
    Examples:
        "BR 11 2012 008823 B8" -> "BR112012008823B8"
        "US 9,376,391 B2" -> "US9376391B2"
    """
    return patent_number.replace(" ", "").replace(",", "").replace("-", "").upper()

def extract_wo_numbers(text: str) -> List[str]:
    """
    Extract WO numbers from text
    
    Pattern: WO followed by year (4 digits) and number (6 digits)
    Examples: WO2011051540, WO2016162604
    """
    pattern = r'WO[\s-]?(\d{4})[\s/]?(\d{6})'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    wo_numbers = []
    for match in matches:
        wo_num = f"WO{match[0]}{match[1]}"
        if wo_num not in wo_numbers:
            wo_numbers.append(wo_num)
    
    return wo_numbers

def get_country_name(country_code: str) -> str:
    """
    Get full country name from code
    
    Args:
        country_code: 2-letter country code (e.g., "BR", "US")
    
    Returns:
        Full country name
    """
    country_names = {
        "BR": "Brazil",
        "US": "United States",
        "EP": "Europe",
        "CN": "China",
        "JP": "Japan",
        "CA": "Canada",
        "AU": "Australia",
        "KR": "South Korea",
        "IN": "India",
        "MX": "Mexico",
        "AR": "Argentina",
        "CL": "Chile",
        "DE": "Germany",
        "FR": "France",
        "GB": "United Kingdom",
        "IT": "Italy",
        "ES": "Spain",
        "RU": "Russia",
        "WO": "WIPO",
    }
    
    return country_names.get(country_code.upper(), country_code)

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"

def is_valid_wo_number(wo_number: str) -> bool:
    """
    Validate WO number format
    
    Valid formats:
        - WO2011051540
        - WO 2011 051540
        - WO2011/051540
    """
    pattern = r'^WO[\s-]?\d{4}[\s/]?\d{6}$'
    return bool(re.match(pattern, wo_number.upper()))

def normalize_wo_number(wo_number: str) -> str:
    """
    Normalize WO number to standard format: WO2011051540
    
    Args:
        wo_number: WO number in any format
    
    Returns:
        Normalized WO number
    """
    # Remove spaces, slashes, hyphens
    clean = wo_number.replace(" ", "").replace("/", "").replace("-", "").upper()
    
    # Extract year and number
    match = re.match(r'WO(\d{4})(\d{6})', clean)
    if match:
        return f"WO{match.group(1)}{match.group(2)}"
    
    return wo_number.upper()

def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def clean_html(text: str) -> str:
    """Remove HTML tags from text"""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()
