"""Google Patents integration via SerpAPI"""
import logging
import aiohttp
from typing import Optional, Dict, Any
from .. import config

logger = logging.getLogger(__name__)

class GooglePatentsClient:
    """Client for Google Patents via SerpAPI"""
    
    def __init__(self):
        self.base_url = config.SERPAPI_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("✅ Google Patents client initialized")
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_patent_details(self, patent_id: str) -> Dict[str, Any]:
        """
        Get full patent details from Google Patents
        
        Args:
            patent_id: Patent number (e.g., "BR112012008823B8", "US9376391B2")
        
        Returns:
            Dictionary with patent details
        """
        await self.initialize()
        
        try:
            # Use SerpAPI engine=google_patents_details
            params = {
                "engine": "google_patents_details",
                "patent_id": patent_id,
                "api_key": config.get_next_serpapi_key()
            }
            
            logger.info(f"🔍 Fetching Google Patents details for {patent_id}")
            
            async with self.session.get(self.base_url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse response
                    result = {
                        "publication_number": patent_id,
                        "title": data.get("title", ""),
                        "abstract": data.get("abstract", ""),
                        "claims": self._extract_claims(data),
                        "assignee": data.get("assignee", ""),
                        "inventors": data.get("inventors", []),
                        "priority_date": data.get("priority_date", ""),
                        "filing_date": data.get("filing_date", ""),
                        "publication_date": data.get("publication_date", ""),
                        "grant_date": data.get("grant_date", ""),
                        "legal_status": data.get("legal_status", ""),
                        "family_id": data.get("family_id", ""),
                        "family_size": data.get("family_size", 0),
                        "cpc_classifications": data.get("cpc_classifications", []),
                        "ipc_classifications": data.get("ipc_classifications", []),
                        "url": data.get("url", f"https://patents.google.com/patent/{patent_id}"),
                        "pdf_url": data.get("pdf_url", ""),
                        "source": "google_patents"
                    }
                    
                    logger.info(f"  ✅ Got details for {patent_id}")
                    return result
                
                else:
                    logger.warning(f"  ⚠️  Google Patents returned {response.status} for {patent_id}")
                    return self._empty_result(patent_id)
        
        except Exception as e:
            logger.error(f"  ❌ Error fetching {patent_id}: {str(e)}")
            return self._empty_result(patent_id)
    
    def _extract_claims(self, data: Dict[str, Any]) -> str:
        """Extract claims text from response"""
        try:
            claims = data.get("claims", [])
            if isinstance(claims, list) and claims:
                # Join all claims
                return "\n\n".join([
                    f"{claim.get('num', '')}. {claim.get('text', '')}"
                    for claim in claims
                ])
            elif isinstance(claims, str):
                return claims
            return ""
        except:
            return ""
    
    def _empty_result(self, patent_id: str) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            "publication_number": patent_id,
            "title": "",
            "abstract": "",
            "claims": "",
            "assignee": "",
            "inventors": [],
            "priority_date": "",
            "filing_date": "",
            "publication_date": "",
            "grant_date": "",
            "legal_status": "",
            "family_id": "",
            "family_size": 0,
            "cpc_classifications": [],
            "ipc_classifications": [],
            "url": f"https://patents.google.com/patent/{patent_id}",
            "pdf_url": "",
            "source": "google_patents"
        }

# Global instance
google_patents_client = GooglePatentsClient()
