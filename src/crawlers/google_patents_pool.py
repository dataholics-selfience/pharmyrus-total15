"""Google Patents Crawler Pool Manager"""
import logging
from typing import List, Optional
from playwright.async_api import async_playwright
from .google_patents_playwright import GooglePatentsCrawler

logger = logging.getLogger(__name__)

class GooglePatentsCrawlerPool:
    """Manages a pool of Google Patents Playwright crawlers"""
    
    def __init__(self, size: int = 2):
        self.size = size
        self.crawlers: List[GooglePatentsCrawler] = []
        self.playwright = None
        self.current = 0
        self.initialized = False
    
    async def initialize(self):
        """Initialize crawler pool with Playwright"""
        if self.initialized:
            logger.warning("Google Patents crawler pool already initialized")
            return
        
        logger.info(f"🔧 Initializing {self.size} Google Patents crawlers...")
        
        try:
            self.playwright = await async_playwright().start()
            
            for i in range(self.size):
                crawler = GooglePatentsCrawler(max_retries=3, timeout=60000)
                await crawler.initialize(self.playwright)
                self.crawlers.append(crawler)
                logger.info(f"  ✅ Google Patents crawler {i+1}/{self.size} ready")
            
            self.initialized = True
            logger.info("✅ Google Patents crawler pool initialized")
        
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Patents crawler pool: {e}")
            raise
    
    async def close(self):
        """Cleanup all crawlers and Playwright"""
        logger.info("🔧 Closing Google Patents crawler pool...")
        
        for crawler in self.crawlers:
            try:
                await crawler.close()
            except Exception as e:
                logger.warning(f"Error closing crawler: {e}")
        
        self.crawlers = []
        
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping Playwright: {e}")
            self.playwright = None
        
        self.initialized = False
        logger.info("✅ Google Patents crawler pool closed")
    
    def get_crawler(self) -> Optional[GooglePatentsCrawler]:
        """Get next available crawler from pool (round-robin)"""
        if not self.initialized or not self.crawlers:
            logger.error("Cannot get crawler: pool not initialized")
            return None
        
        crawler = self.crawlers[self.current]
        self.current = (self.current + 1) % len(self.crawlers)
        return crawler
    
    async def fetch_patent(self, patent_id: str) -> dict:
        """Fetch patent details using an available crawler"""
        crawler = self.get_crawler()
        if not crawler:
            return {
                'error': 'Crawler pool not initialized',
                'publication_number': patent_id
            }
        
        return await crawler.fetch_patent_details(patent_id)

# Global instance
google_patents_pool = GooglePatentsCrawlerPool(size=2)
