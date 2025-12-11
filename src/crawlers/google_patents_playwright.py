"""Google Patents Crawler using Playwright - Direct HTML parsing"""
import asyncio
import random
import logging
from typing import Dict, Any, List, Optional, Tuple
from playwright.async_api import Page, Browser, BrowserContext
from datetime import datetime

logger = logging.getLogger(__name__)

class GooglePatentsCrawler:
    """Direct crawler for Google Patents without API dependencies"""
    
    def __init__(self, max_retries: int = 3, timeout: int = 60000):
        self.max_retries = max_retries
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def initialize(self, playwright):
        """Initialize browser and context"""
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        logger.info("✅ Google Patents Playwright crawler initialized")
    
    async def close(self):
        """Cleanup resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    def _normalize_patent_id(self, patent_id: str) -> str:
        """Normalize patent ID format"""
        return patent_id.upper().replace(' ', '').replace('-', '')
    
    async def _extract_basic_info(self, page: Page) -> Dict[str, Any]:
        """Extract basic patent information"""
        data = {
            'title': '',
            'abstract': '',
            'assignee': '',
            'inventors': [],
            'filing_date': '',
            'publication_date': '',
            'grant_date': '',
            'priority_date': '',
            'legal_status': '',
            'classifications': {'cpc': [], 'ipc': []},
            'pdf_url': ''
        }
        
        # Title
        try:
            title_elem = await page.query_selector('span[itemprop="title"]')
            if not title_elem:
                title_elem = await page.query_selector('h1#title')
            if title_elem:
                data['title'] = (await title_elem.inner_text()).strip()
                logger.info(f"    ✅ Title: {data['title'][:50]}...")
        except Exception as e:
            logger.warning(f"    ⚠️  Could not extract title: {e}")
        
        # Abstract
        try:
            abstract_elem = await page.query_selector('div.abstract')
            if abstract_elem:
                data['abstract'] = (await abstract_elem.inner_text()).strip()
                logger.info(f"    ✅ Abstract: {len(data['abstract'])} chars")
        except Exception as e:
            logger.warning(f"    ⚠️  Could not extract abstract: {e}")
        
        # Assignee
        try:
            assignee_elem = await page.query_selector('dd[itemprop="assigneeCurrent"]')
            if not assignee_elem:
                assignee_elem = await page.query_selector('dd.assignee')
            if assignee_elem:
                data['assignee'] = (await assignee_elem.inner_text()).strip()
                logger.info(f"    ✅ Assignee: {data['assignee']}")
        except Exception as e:
            logger.warning(f"    ⚠️  Could not extract assignee: {e}")
        
        # Inventors
        try:
            inventor_elems = await page.query_selector_all('dd[itemprop="inventor"]')
            for elem in inventor_elems:
                inventor = (await elem.inner_text()).strip()
                if inventor:
                    data['inventors'].append(inventor)
            if data['inventors']:
                logger.info(f"    ✅ Inventors: {len(data['inventors'])} found")
        except Exception as e:
            logger.warning(f"    ⚠️  Could not extract inventors: {e}")
        
        # Dates
        date_mappings = {
            'filing_date': ['Filing date', 'Application filed'],
            'publication_date': ['Publication date', 'Published'],
            'grant_date': ['Grant date', 'Granted'],
            'priority_date': ['Priority date', 'Priority']
        }
        
        for field, labels in date_mappings.items():
            try:
                for label in labels:
                    date_elem = await page.query_selector(f'dt:has-text("{label}") + dd')
                    if date_elem:
                        date_text = (await date_elem.inner_text()).strip()
                        # Extract date in format YYYY-MM-DD
                        if date_text and len(date_text) >= 10:
                            data[field] = date_text[:10]
                            break
            except Exception as e:
                logger.warning(f"    ⚠️  Could not extract {field}: {e}")
        
        # Classifications
        try:
            # CPC
            cpc_elems = await page.query_selector_all('span.cpc')
            for elem in cpc_elems[:10]:  # Limit to 10
                cpc = (await elem.inner_text()).strip()
                if cpc:
                    data['classifications']['cpc'].append(cpc)
            
            # IPC
            ipc_elems = await page.query_selector_all('span.ipc')
            for elem in ipc_elems[:10]:  # Limit to 10
                ipc = (await elem.inner_text()).strip()
                if ipc:
                    data['classifications']['ipc'].append(ipc)
            
            if data['classifications']['cpc'] or data['classifications']['ipc']:
                logger.info(f"    ✅ Classifications: {len(data['classifications']['cpc'])} CPC, {len(data['classifications']['ipc'])} IPC")
        except Exception as e:
            logger.warning(f"    ⚠️  Could not extract classifications: {e}")
        
        # PDF URL
        try:
            pdf_elem = await page.query_selector('a[href*=".pdf"]')
            if pdf_elem:
                data['pdf_url'] = await pdf_elem.get_attribute('href')
                if data['pdf_url'] and not data['pdf_url'].startswith('http'):
                    data['pdf_url'] = 'https://patents.google.com' + data['pdf_url']
        except Exception as e:
            logger.warning(f"    ⚠️  Could not extract PDF URL: {e}")
        
        # Legal Status
        try:
            status_elem = await page.query_selector('span.legal-status')
            if not status_elem:
                status_elem = await page.query_selector('dd.status')
            if status_elem:
                data['legal_status'] = (await status_elem.inner_text()).strip()
        except Exception as e:
            logger.warning(f"    ⚠️  Could not extract legal status: {e}")
        
        return data
    
    async def _extract_patent_family(self, page: Page) -> List[Dict[str, Any]]:
        """Extract patent family members (worldwide applications)"""
        family_members = []
        
        try:
            # Click on "Patent family" tab if exists
            family_tab = await page.query_selector('a:has-text("Patent family")')
            if not family_tab:
                family_tab = await page.query_selector('a:has-text("Family")')
            
            if family_tab:
                await family_tab.click()
                await page.wait_for_timeout(2000)  # Wait for content to load
                logger.info("    ✅ Clicked Patent Family tab")
            
            # Extract family members from table
            rows = await page.query_selector_all('table.patent-family tr')
            
            for row in rows:
                try:
                    cells = await row.query_selector_all('td')
                    if len(cells) >= 3:
                        # Extract publication number
                        pub_elem = await cells[0].query_selector('a')
                        if pub_elem:
                            pub_number = (await pub_elem.inner_text()).strip()
                            pub_link = await pub_elem.get_attribute('href')
                            
                            # Extract country code from publication number
                            country_code = pub_number[:2] if len(pub_number) >= 2 else ''
                            
                            # Extract filing date
                            filing_date = (await cells[1].inner_text()).strip() if len(cells) > 1 else ''
                            
                            # Extract title
                            title = (await cells[2].inner_text()).strip() if len(cells) > 2 else ''
                            
                            member = {
                                'publication_number': pub_number,
                                'country_code': country_code,
                                'filing_date': filing_date,
                                'title': title,
                                'link': f"https://patents.google.com{pub_link}" if pub_link and not pub_link.startswith('http') else pub_link
                            }
                            
                            family_members.append(member)
                except Exception as e:
                    logger.warning(f"    ⚠️  Error parsing family member row: {e}")
                    continue
            
            if family_members:
                logger.info(f"    ✅ Found {len(family_members)} family members")
            else:
                logger.warning("    ⚠️  No patent family members found")
        
        except Exception as e:
            logger.warning(f"    ⚠️  Could not extract patent family: {e}")
        
        return family_members
    
    async def fetch_patent_details(self, patent_id: str) -> Dict[str, Any]:
        """
        Fetch complete patent details from Google Patents
        
        Args:
            patent_id: Patent publication number (e.g., "BR112012008823B8", "US20130123456A1")
        
        Returns:
            Dictionary with patent details and family information
        """
        clean_id = self._normalize_patent_id(patent_id)
        url = f"https://patents.google.com/patent/{clean_id}/en"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔍 Fetching Google Patents details for {clean_id} (attempt {attempt + 1}/{self.max_retries})")
                
                page = await self.context.new_page()
                
                # Navigate to patent page
                response = await page.goto(url, timeout=self.timeout, wait_until='networkidle')
                
                if response.status == 404:
                    logger.warning(f"    ⚠️  Patent {clean_id} not found (404)")
                    await page.close()
                    return self._empty_result(clean_id, "Patent not found")
                
                # Wait for content to load
                await page.wait_for_timeout(2000)
                
                # Extract basic information
                basic_info = await self._extract_basic_info(page)
                
                # Extract patent family
                family_members = await self._extract_patent_family(page)
                
                await page.close()
                
                # Check if we got meaningful data
                if not any([basic_info['title'], basic_info['abstract'], family_members]):
                    if attempt < self.max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"    ⚠️  No data extracted, retrying in {wait_time:.1f}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"    ❌ Failed to extract data after {self.max_retries} attempts")
                        return self._empty_result(clean_id, "No data extracted")
                
                # Build result
                result = {
                    'source': 'google_patents_playwright',
                    'publication_number': clean_id,
                    'url': url,
                    'title': basic_info['title'],
                    'abstract': basic_info['abstract'],
                    'assignee': basic_info['assignee'],
                    'inventors': basic_info['inventors'],
                    'filing_date': basic_info['filing_date'],
                    'publication_date': basic_info['publication_date'],
                    'grant_date': basic_info['grant_date'],
                    'priority_date': basic_info['priority_date'],
                    'legal_status': basic_info['legal_status'],
                    'classifications': basic_info['classifications'],
                    'pdf_url': basic_info['pdf_url'],
                    'patent_family': {
                        'total_members': len(family_members),
                        'members': family_members,
                        'countries': list(set(m['country_code'] for m in family_members if m['country_code']))
                    },
                    'extracted_at': datetime.utcnow().isoformat(),
                    'attempt': attempt + 1
                }
                
                logger.info(f"✅ Successfully extracted {clean_id}: {len(family_members)} family members")
                return result
            
            except Exception as e:
                logger.error(f"    ❌ Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(wait_time)
                else:
                    return self._empty_result(clean_id, str(e))
        
        return self._empty_result(clean_id, "Max retries exceeded")
    
    def _empty_result(self, patent_id: str, error: str) -> Dict[str, Any]:
        """Return empty result structure on error"""
        return {
            'source': 'google_patents_playwright',
            'publication_number': patent_id,
            'url': f"https://patents.google.com/patent/{patent_id}/en",
            'title': '',
            'abstract': '',
            'assignee': '',
            'inventors': [],
            'filing_date': '',
            'publication_date': '',
            'grant_date': '',
            'priority_date': '',
            'legal_status': '',
            'classifications': {'cpc': [], 'ipc': []},
            'pdf_url': '',
            'patent_family': {
                'total_members': 0,
                'members': [],
                'countries': []
            },
            'error': error,
            'extracted_at': datetime.utcnow().isoformat()
        }
