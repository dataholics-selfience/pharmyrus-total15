"""Configuration for Pharmyrus v4.0"""
import os
from typing import List

# SerpAPI - Rotation of 9 keys (250 queries each = 2,250 total/month)
SERPAPI_KEYS: List[str] = [
    "bc20bca64032a7ac59abf330bbdeca80aa79cd72bb208059056b10fb6e33e4bc",
    "3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d",
    # Add your other 7 keys here when available
    "key3",
    "key4",
    "key5",
    "key6",
    "key7",
    "key8",
    "key9"
]

# Current key index (rotates automatically)
_current_serpapi_key_index = 0

def get_next_serpapi_key() -> str:
    """Get next SerpAPI key in rotation"""
    global _current_serpapi_key_index
    key = SERPAPI_KEYS[_current_serpapi_key_index]
    _current_serpapi_key_index = (_current_serpapi_key_index + 1) % len(SERPAPI_KEYS)
    return key

# WIPO Patentscope
WIPO_BASE_URL = "https://patentscope.wipo.int"
WIPO_SEARCH_URL = f"{WIPO_BASE_URL}/search/en/detail.jsf"

# Google Patents via SerpAPI
SERPAPI_BASE_URL = "https://serpapi.com/search.json"

# INPI Brasil API
INPI_API_URL = os.getenv("INPI_API_URL", "https://crawler3-production.up.railway.app/api/data/inpi/patents")

# PubChem
PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

# EPO OPS API (optional)
EPO_CONSUMER_KEY = os.getenv("EPO_CONSUMER_KEY", "")
EPO_CONSUMER_SECRET = os.getenv("EPO_CONSUMER_SECRET", "")
EPO_BASE_URL = "https://ops.epo.org/3.2"

# Crawler Pool Settings
CRAWLER_POOL_SIZE = int(os.getenv("CRAWLER_POOL_SIZE", "2"))
CRAWLER_TIMEOUT = int(os.getenv("CRAWLER_TIMEOUT", "60000"))  # 60 seconds
CRAWLER_MAX_RETRIES = int(os.getenv("CRAWLER_MAX_RETRIES", "3"))

# Rate Limiting
DELAY_BETWEEN_WOS = float(os.getenv("DELAY_BETWEEN_WOS", "2.0"))  # seconds
DELAY_BETWEEN_QUERIES = float(os.getenv("DELAY_BETWEEN_QUERIES", "1.0"))  # seconds

# Search Settings
MAX_WOS_DEFAULT = int(os.getenv("MAX_WOS_DEFAULT", "10"))
MAX_PATENTS_PER_WO = int(os.getenv("MAX_PATENTS_PER_WO", "100"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
