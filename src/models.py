"""Pydantic models for Pharmyrus v4.0"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ============================================================================
# ENDPOINT 1: WO Details Models
# ============================================================================

class WorldwideApplication(BaseModel):
    """Single worldwide application from a WO patent"""
    country_code: str
    application_number: str
    filing_date: Optional[str] = None
    publication_date: Optional[str] = None
    status: Optional[str] = None

class WODetailsResponse(BaseModel):
    """Response for GET /api/v1/wo/{wo_number}"""
    wo_number: str
    title: Optional[str] = None
    abstract: Optional[str] = None
    assignee: Optional[str] = None
    filing_date: Optional[str] = None
    publication_date: Optional[str] = None
    
    worldwide_applications: Dict[str, List[WorldwideApplication]] = Field(
        default_factory=dict,
        description="Applications grouped by year"
    )
    
    total_applications: int = 0
    total_countries: int = 0
    
    search_duration_seconds: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

# ============================================================================
# ENDPOINT 2: Patent Details Models
# ============================================================================

class GooglePatentsSource(BaseModel):
    """Google Patents data source"""
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    cpc_classifications: List[str] = Field(default_factory=list)
    ipc_classifications: List[str] = Field(default_factory=list)
    family_id: Optional[str] = None
    family_size: Optional[int] = None

class INPISource(BaseModel):
    """INPI Brasil data source"""
    status: Optional[str] = None
    process_number: Optional[str] = None
    events: List[Dict[str, Any]] = Field(default_factory=list)
    rpi_publications: List[Dict[str, Any]] = Field(default_factory=list)

class PatentDetailsResponse(BaseModel):
    """Response for GET /api/v1/patent/{patent_number}"""
    publication_number: str
    country_code: str
    
    # Dates
    priority_date: Optional[str] = None
    filing_date: Optional[str] = None
    publication_date: Optional[str] = None
    grant_date: Optional[str] = None
    
    # Content
    title: Optional[str] = None
    abstract: Optional[str] = None
    claims: Optional[str] = None
    
    # Parties
    assignee: Optional[str] = None
    inventors: List[str] = Field(default_factory=list)
    
    # Legal
    legal_status: Optional[str] = None
    legal_status_detail: Optional[str] = None
    
    # Family
    family_id: Optional[str] = None
    wo_number: Optional[str] = None
    
    # Sources
    sources: Dict[str, Any] = Field(default_factory=dict)
    
    search_duration_seconds: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

# ============================================================================
# ENDPOINT 3: Search Models
# ============================================================================

class SearchRequest(BaseModel):
    """Request for POST /api/v1/search"""
    molecule_name: str = Field(..., description="Molecule name (e.g., 'darolutamide')")
    max_wos: int = Field(default=10, ge=1, le=50, description="Maximum WO numbers to process")
    include_inpi: bool = Field(default=True, description="Include INPI enrichment for BR patents")
    include_epo: bool = Field(default=False, description="Include EPO family data")

class ExecutiveSummary(BaseModel):
    """Executive summary for search results"""
    molecule_name: str
    generic_name: Optional[str] = None
    commercial_name: Optional[str] = None
    
    total_patents: int = 0
    total_families: int = 0
    
    jurisdictions: Dict[str, int] = Field(default_factory=dict)
    patent_types: Dict[str, int] = Field(default_factory=dict)
    
    consistency_score: float = 1.0
    search_duration_seconds: float = 0.0

class Patent(BaseModel):
    """Individual patent in search results"""
    publication_number: str
    country_code: str
    
    # Dates
    priority_number: Optional[str] = None
    priority_date: Optional[str] = None
    filing_date: Optional[str] = None
    publication_date: Optional[str] = None
    grant_date: Optional[str] = None
    
    # Content
    title: Optional[str] = None
    abstract: Optional[str] = None
    claims: Optional[str] = None
    
    # Parties
    assignee: Optional[str] = None
    inventors: List[str] = Field(default_factory=list)
    
    # Jurisdiction
    jurisdiction: str
    jurisdiction_name: str
    legal_status: Optional[str] = None
    legal_status_detail: Optional[str] = None
    
    # Family
    family_id: Optional[str] = None
    family_size: Optional[int] = None
    
    # Classifications
    cpc_classifications: List[str] = Field(default_factory=list)
    ipc_classifications: List[str] = Field(default_factory=list)
    
    # Source
    source: str
    source_url: Optional[str] = None
    pdf_url: Optional[str] = None
    
    # INPI (if BR)
    inpi_enriched: bool = False
    inpi_status: Optional[str] = None
    inpi_process_number: Optional[str] = None

class SearchMetadata(BaseModel):
    """Metadata about the search execution"""
    query_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    sources_used: List[str] = Field(default_factory=list)
    wo_numbers_found: int = 0
    wo_numbers_processed: int = 0
    serpapi_queries_used: int = 0
    errors_count: int = 0
    warnings: List[str] = Field(default_factory=list)

class SearchResponse(BaseModel):
    """Response for POST /api/v1/search (target-buscas.json format)"""
    executive_summary: ExecutiveSummary
    patents: List[Patent] = Field(default_factory=list)
    search_metadata: SearchMetadata

# ============================================================================
# Helper Models
# ============================================================================

class PubChemData(BaseModel):
    """PubChem molecule data"""
    molecule_name: str
    dev_codes: List[str] = Field(default_factory=list)
    cas_number: Optional[str] = None
    synonyms: List[str] = Field(default_factory=list)
    molecular_formula: Optional[str] = None
    smiles: Optional[str] = None

class WODiscoveryResult(BaseModel):
    """Result from WO number discovery"""
    wo_numbers: List[str] = Field(default_factory=list)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    sources: List[str] = Field(default_factory=list)
