"""Search orchestrator - Complete pipeline"""
import logging
import asyncio
import time
from typing import List, Dict, Any
from collections import defaultdict

from .models import (
    SearchRequest,
    SearchResponse,
    ExecutiveSummary,
    Patent,
    SearchMetadata
)
from .discovery import pubchem_client, wo_discovery_service
from .crawlers import crawler_pool, google_patents_client, inpi_client
from . import config, utils

logger = logging.getLogger(__name__)

class SearchOrchestrator:
    """Orchestrate complete patent search pipeline"""
    
    async def execute_search(self, request: SearchRequest) -> SearchResponse:
        """
        Execute complete search pipeline
        
        Pipeline:
        1. PubChem → dev codes, CAS, synonyms
        2. WO Discovery → find WO numbers
        3. For each WO → WIPO Crawler → worldwide applications
        4. For each application → Google Patents → full details
        5. For each BR → INPI → enrichment
        6. Consolidation → final JSON
        """
        start_time = time.time()
        
        logger.info("=" * 80)
        logger.info(f"🚀 STARTING SEARCH PIPELINE: {request.molecule_name}")
        logger.info("=" * 80)
        
        # Initialize services
        await pubchem_client.initialize()
        await wo_discovery_service.initialize()
        
        patents: List[Patent] = []
        sources_used = []
        errors_count = 0
        warnings = []
        serpapi_queries = 0
        
        try:
            # ================================================================
            # PHASE 1: PubChem - Get molecule data
            # ================================================================
            logger.info("\n📊 PHASE 1: PubChem")
            logger.info("-" * 80)
            
            pubchem_data = await pubchem_client.get_molecule_data(request.molecule_name)
            sources_used.append("PubChem")
            
            logger.info(f"  Dev codes: {len(pubchem_data.dev_codes)}")
            logger.info(f"  CAS: {pubchem_data.cas_number or 'N/A'}")
            logger.info(f"  Synonyms: {len(pubchem_data.synonyms)}")
            
            # ================================================================
            # PHASE 2: WO Discovery - Find WO numbers
            # ================================================================
            logger.info("\n🔍 PHASE 2: WO Discovery")
            logger.info("-" * 80)
            
            wo_result = await wo_discovery_service.discover_wo_numbers(
                request.molecule_name,
                pubchem_data,
                max_results=request.max_wos
            )
            
            sources_used.extend(wo_result.sources)
            serpapi_queries += len(wo_result.sources) * 2  # Estimate
            
            wo_numbers = wo_result.wo_numbers[:request.max_wos]
            
            logger.info(f"  Found {len(wo_numbers)} WO numbers")
            for i, wo in enumerate(wo_numbers[:5], 1):
                logger.info(f"    {i}. {wo}")
            if len(wo_numbers) > 5:
                logger.info(f"    ... and {len(wo_numbers) - 5} more")
            
            if not wo_numbers:
                warnings.append("No WO numbers found")
                logger.warning("  ⚠️  No WO numbers found!")
            
            # ================================================================
            # PHASE 3: Process each WO
            # ================================================================
            logger.info("\n🌍 PHASE 3: Processing WO patents")
            logger.info("-" * 80)
            
            all_applications = []
            
            for idx, wo_number in enumerate(wo_numbers, 1):
                logger.info(f"\n  [{idx}/{len(wo_numbers)}] Processing {wo_number}")
                
                try:
                    # Get crawler
                    crawler = crawler_pool.get_crawler()
                    
                    # Fetch WO details
                    wo_data = await crawler.get_wo_details(wo_number)
                    
                    if not wo_data:
                        logger.warning(f"    ⚠️  No data for {wo_number}")
                        errors_count += 1
                        continue
                    
                    # Extract worldwide applications
                    worldwide_apps = wo_data.get("worldwide_applications", {})
                    
                    for year, apps in worldwide_apps.items():
                        all_applications.extend(apps)
                    
                    logger.info(f"    ✅ Found {len(all_applications)} applications")
                    
                    # Rate limiting
                    if idx < len(wo_numbers):
                        await asyncio.sleep(config.DELAY_BETWEEN_WOS)
                
                except Exception as e:
                    logger.error(f"    ❌ Error: {str(e)}")
                    errors_count += 1
            
            sources_used.append("WIPO")
            
            logger.info(f"\n  Total applications collected: {len(all_applications)}")
            
            # ================================================================
            # PHASE 4: Enrich each application with Google Patents
            # ================================================================
            logger.info("\n📚 PHASE 4: Enriching with Google Patents")
            logger.info("-" * 80)
            
            # Limit to prevent timeout
            max_patents = min(len(all_applications), 50)
            applications_to_process = all_applications[:max_patents]
            
            if len(all_applications) > max_patents:
                warnings.append(f"Limited to {max_patents} patents (found {len(all_applications)})")
                logger.warning(f"  ⚠️  Limiting to {max_patents} patents")
            
            for idx, app in enumerate(applications_to_process, 1):
                patent_number = app.get("application_number", "")
                country_code = app.get("country_code", "")
                
                if not patent_number:
                    continue
                
                logger.info(f"  [{idx}/{len(applications_to_process)}] {patent_number}")
                
                try:
                    # Get Google Patents details
                    gp_data = await google_patents_client.get_patent_details(patent_number)
                    serpapi_queries += 1
                    
                    # Create Patent object
                    patent = Patent(
                        publication_number=patent_number,
                        country_code=country_code,
                        priority_date=gp_data.get("priority_date", ""),
                        filing_date=gp_data.get("filing_date", "") or app.get("filing_date", ""),
                        publication_date=gp_data.get("publication_date", ""),
                        grant_date=gp_data.get("grant_date", ""),
                        title=gp_data.get("title", ""),
                        abstract=gp_data.get("abstract", ""),
                        claims=gp_data.get("claims", ""),
                        assignee=gp_data.get("assignee", ""),
                        inventors=gp_data.get("inventors", []),
                        jurisdiction=country_code,
                        jurisdiction_name=utils.get_country_name(country_code),
                        legal_status=gp_data.get("legal_status", ""),
                        family_id=gp_data.get("family_id", ""),
                        family_size=gp_data.get("family_size", 0),
                        cpc_classifications=gp_data.get("cpc_classifications", []),
                        ipc_classifications=gp_data.get("ipc_classifications", []),
                        source="google_patents",
                        source_url=gp_data.get("url", ""),
                        pdf_url=gp_data.get("pdf_url", ""),
                        inpi_enriched=False
                    )
                    
                    # PHASE 5: INPI enrichment for BR patents
                    if country_code == "BR" and request.include_inpi:
                        try:
                            inpi_data = await inpi_client.get_patent_details(patent_number)
                            
                            if inpi_data.get("found"):
                                patent.inpi_enriched = True
                                patent.inpi_status = inpi_data.get("status", "")
                                patent.inpi_process_number = inpi_data.get("process_number", "")
                                
                                # Enrich with INPI data
                                if not patent.title and inpi_data.get("title"):
                                    patent.title = inpi_data["title"]
                                if not patent.assignee and inpi_data.get("applicant"):
                                    patent.assignee = inpi_data["applicant"]
                        
                        except Exception as e:
                            logger.error(f"    ⚠️  INPI error: {str(e)}")
                    
                    patents.append(patent)
                    
                    # Rate limiting
                    await asyncio.sleep(config.DELAY_BETWEEN_QUERIES)
                
                except Exception as e:
                    logger.error(f"    ❌ Error: {str(e)}")
                    errors_count += 1
            
            sources_used.append("Google Patents")
            if request.include_inpi:
                sources_used.append("INPI")
            
            # ================================================================
            # PHASE 6: Generate Executive Summary
            # ================================================================
            logger.info("\n📊 PHASE 6: Generating Summary")
            logger.info("-" * 80)
            
            # Count jurisdictions
            jurisdictions = defaultdict(int)
            for patent in patents:
                jurisdictions[patent.country_code] += 1
            
            # Count families
            families = set(p.family_id for p in patents if p.family_id)
            
            duration = time.time() - start_time
            
            executive_summary = ExecutiveSummary(
                molecule_name=request.molecule_name,
                generic_name=pubchem_data.molecule_name,
                commercial_name=request.molecule_name,
                total_patents=len(patents),
                total_families=len(families),
                jurisdictions=dict(jurisdictions),
                patent_types={},  # Future: inference
                consistency_score=1.0,
                search_duration_seconds=round(duration, 2)
            )
            
            # Metadata
            metadata = SearchMetadata(
                sources_used=list(set(sources_used)),
                wo_numbers_found=len(wo_result.wo_numbers),
                wo_numbers_processed=len(wo_numbers),
                serpapi_queries_used=serpapi_queries,
                errors_count=errors_count,
                warnings=warnings
            )
            
            # ================================================================
            # Final Response
            # ================================================================
            logger.info("\n" + "=" * 80)
            logger.info("✅ SEARCH COMPLETE")
            logger.info("=" * 80)
            logger.info(f"  Total patents: {len(patents)}")
            logger.info(f"  Jurisdictions: {len(jurisdictions)}")
            logger.info(f"  Families: {len(families)}")
            logger.info(f"  Duration: {utils.format_duration(duration)}")
            logger.info(f"  SerpAPI queries: {serpapi_queries}")
            logger.info(f"  Errors: {errors_count}")
            logger.info("=" * 80 + "\n")
            
            return SearchResponse(
                executive_summary=executive_summary,
                patents=patents,
                search_metadata=metadata
            )
        
        except Exception as e:
            logger.error(f"❌ PIPELINE ERROR: {str(e)}")
            raise

# Global instance
search_orchestrator = SearchOrchestrator()
