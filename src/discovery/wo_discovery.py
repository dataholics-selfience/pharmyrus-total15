"""WO number discovery from multiple sources"""
import logging
import aiohttp
import asyncio
from typing import List, Set
from ..models import WODiscoveryResult, PubChemData
from .. import config, utils

logger = logging.getLogger(__name__)

class WODiscoveryService:
    """Service to discover WO numbers from multiple sources"""
    
    def __init__(self):
        self.session: aiohttp.ClientSession = None
    
    async def initialize(self):
        """Initialize session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("✅ WO Discovery service initialized")
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def discover_wo_numbers(
        self,
        molecule_name: str,
        pubchem_data: PubChemData,
        max_results: int = 20
    ) -> WODiscoveryResult:
        """
        Discover WO numbers from multiple sources
        
        Strategy:
        1. Google Patents search (molecule name)
        2. Google Patents search (dev codes)
        3. Google search (molecule + patent)
        4. Deduplicate and rank
        """
        await self.initialize()
        
        logger.info(f"🔍 Discovering WO numbers for {molecule_name}")
        
        all_wo_numbers: Set[str] = set()
        sources_used = []
        
        # Source 1: Google Patents - molecule name
        logger.info(f"  📚 Source 1: Google Patents (molecule)")
        wos = await self._search_google_patents(molecule_name)
        all_wo_numbers.update(wos)
        if wos:
            sources_used.append("google_patents_molecule")
        
        # Source 2: Google Patents - dev codes
        if pubchem_data.dev_codes:
            logger.info(f"  📚 Source 2: Google Patents ({len(pubchem_data.dev_codes)} dev codes)")
            for dev_code in pubchem_data.dev_codes[:5]:  # Limit to first 5
                await asyncio.sleep(config.DELAY_BETWEEN_QUERIES)
                wos = await self._search_google_patents(dev_code)
                all_wo_numbers.update(wos)
            if wos:
                sources_used.append("google_patents_dev_codes")
        
        # Source 3: Google search (molecule + WO)
        logger.info(f"  📚 Source 3: Google search")
        wos = await self._search_google(molecule_name)
        all_wo_numbers.update(wos)
        if wos:
            sources_used.append("google_search")
        
        # Convert to sorted list
        wo_list = sorted(list(all_wo_numbers), reverse=True)[:max_results]
        
        logger.info(f"  ✅ Found {len(wo_list)} unique WO numbers")
        
        return WODiscoveryResult(
            wo_numbers=wo_list,
            confidence_scores={wo: 1.0 for wo in wo_list},
            sources=sources_used
        )
    
    async def _search_google_patents(self, query: str) -> Set[str]:
        """Search Google Patents via SerpAPI"""
        try:
            params = {
                "engine": "google_patents",
                "q": query,
                "api_key": config.get_next_serpapi_key(),
                "num": 20
            }
            
            async with self.session.get(config.SERPAPI_BASE_URL, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    wo_numbers = set()
                    results = data.get("organic_results", [])
                    
                    for result in results:
                        # Extract from title, snippet, patent_id
                        text = (
                            result.get("title", "") + " " +
                            result.get("snippet", "") + " " +
                            result.get("patent_id", "")
                        )
                        
                        wos = utils.extract_wo_numbers(text)
                        wo_numbers.update(wos)
                    
                    return wo_numbers
        
        except Exception as e:
            logger.error(f"    ❌ Google Patents error: {str(e)}")
        
        return set()
    
    async def _search_google(self, query: str) -> Set[str]:
        """Search Google via SerpAPI"""
        try:
            search_query = f"{query} patent WO"
            
            params = {
                "engine": "google",
                "q": search_query,
                "api_key": config.get_next_serpapi_key(),
                "num": 10
            }
            
            async with self.session.get(config.SERPAPI_BASE_URL, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    wo_numbers = set()
                    results = data.get("organic_results", [])
                    
                    for result in results:
                        text = (
                            result.get("title", "") + " " +
                            result.get("snippet", "") + " " +
                            result.get("link", "")
                        )
                        
                        wos = utils.extract_wo_numbers(text)
                        wo_numbers.update(wos)
                    
                    return wo_numbers
        
        except Exception as e:
            logger.error(f"    ❌ Google search error: {str(e)}")
        
        return set()

# Global instance
wo_discovery_service = WODiscoveryService()
