"""INPI Brasil API integration"""
import logging
import aiohttp
from typing import Optional, Dict, Any, List
from .. import config

logger = logging.getLogger(__name__)

class INPIClient:
    """Client for INPI Brasil API"""
    
    def __init__(self):
        self.base_url = config.INPI_API_URL
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("✅ INPI client initialized")
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_patent_details(self, br_number: str) -> Dict[str, Any]:
        """
        Get BR patent details from INPI API
        
        Args:
            br_number: BR patent number (e.g., "BR112012008823")
        
        Returns:
            Dictionary with INPI data
        """
        await self.initialize()
        
        # Clean BR number (remove spaces, hyphens)
        clean_number = br_number.replace(" ", "").replace("-", "").upper()
        
        # Extract just the number part
        if clean_number.startswith("BR"):
            medicine_query = clean_number[2:]  # Remove "BR" prefix
        else:
            medicine_query = clean_number
        
        try:
            # INPI API: ?medicine={number}
            params = {"medicine": medicine_query}
            
            logger.info(f"🔍 Fetching INPI details for {br_number}")
            
            async with self.session.get(self.base_url, params=params, timeout=60) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse INPI response
                    result = self._parse_inpi_response(data, br_number)
                    
                    if result.get("found"):
                        logger.info(f"  ✅ Got INPI data for {br_number}")
                    else:
                        logger.warning(f"  ⚠️  No INPI data found for {br_number}")
                    
                    return result
                
                else:
                    logger.warning(f"  ⚠️  INPI API returned {response.status} for {br_number}")
                    return self._empty_result(br_number)
        
        except Exception as e:
            logger.error(f"  ❌ Error fetching INPI {br_number}: {str(e)}")
            return self._empty_result(br_number)
    
    def _parse_inpi_response(self, data: Dict[str, Any], br_number: str) -> Dict[str, Any]:
        """Parse INPI API response"""
        try:
            # INPI API returns: {"data": [...], "status": "success"}
            patents = data.get("data", [])
            
            if not patents:
                return self._empty_result(br_number)
            
            # Find matching patent (usually first one)
            patent = patents[0]
            
            result = {
                "found": True,
                "publication_number": br_number,
                "status": patent.get("status", ""),
                "process_number": patent.get("processNumber", ""),
                "title": patent.get("title", ""),
                "applicant": patent.get("applicant", ""),
                "deposit_date": patent.get("depositDate", ""),
                "publication_date": patent.get("publicationDate", ""),
                "full_text": patent.get("fullText", ""),
                "events": self._parse_events(patent.get("events", [])),
                "source": "inpi_brasil"
            }
            
            return result
        
        except Exception as e:
            logger.error(f"  ❌ Error parsing INPI response: {str(e)}")
            return self._empty_result(br_number)
    
    def _parse_events(self, events: Any) -> List[Dict[str, str]]:
        """Parse INPI events"""
        try:
            if isinstance(events, list):
                return [
                    {
                        "date": event.get("date", ""),
                        "event_type": event.get("type", ""),
                        "description": event.get("description", "")
                    }
                    for event in events
                ]
            return []
        except:
            return []
    
    def _empty_result(self, br_number: str) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            "found": False,
            "publication_number": br_number,
            "status": "",
            "process_number": "",
            "title": "",
            "applicant": "",
            "deposit_date": "",
            "publication_date": "",
            "full_text": "",
            "events": [],
            "source": "inpi_brasil"
        }

# Global instance
inpi_client = INPIClient()
