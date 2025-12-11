"""PubChem integration for molecule data"""
import logging
import aiohttp
from typing import Dict, Any, List
from ..models import PubChemData

logger = logging.getLogger(__name__)

class PubChemClient:
    """Client for PubChem REST API"""
    
    def __init__(self):
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.session: aiohttp.ClientSession = None
    
    async def initialize(self):
        """Initialize session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("✅ PubChem client initialized")
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_molecule_data(self, molecule_name: str) -> PubChemData:
        """
        Get molecule data from PubChem
        
        Returns:
            - dev_codes: Development codes (e.g., ODM-201, ARN-509)
            - cas_number: CAS registry number
            - synonyms: List of synonyms
            - molecular_formula: Chemical formula
        """
        await self.initialize()
        
        logger.info(f"🔍 Fetching PubChem data for {molecule_name}")
        
        try:
            # Get synonyms
            url = f"{self.base_url}/compound/name/{molecule_name}/synonyms/JSON"
            
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    logger.warning(f"  ⚠️  PubChem returned {response.status}")
                    return self._empty_result(molecule_name)
                
                data = await response.json()
                
                # Parse response
                info = data.get("InformationList", {}).get("Information", [])
                if not info:
                    return self._empty_result(molecule_name)
                
                synonyms = info[0].get("Synonym", [])
                
                # Extract dev codes
                dev_codes = self._extract_dev_codes(synonyms)
                
                # Extract CAS number
                cas_number = self._extract_cas_number(synonyms)
                
                # Filter synonyms (remove duplicates, too long, etc)
                filtered_synonyms = self._filter_synonyms(synonyms)
                
                logger.info(f"  ✅ Found {len(dev_codes)} dev codes, CAS: {cas_number or 'N/A'}")
                
                # Get additional properties
                molecular_formula = await self._get_molecular_formula(molecule_name)
                smiles = await self._get_smiles(molecule_name)
                
                return PubChemData(
                    molecule_name=molecule_name,
                    dev_codes=dev_codes,
                    cas_number=cas_number,
                    synonyms=filtered_synonyms,
                    molecular_formula=molecular_formula,
                    smiles=smiles
                )
        
        except Exception as e:
            logger.error(f"  ❌ PubChem error: {str(e)}")
            return self._empty_result(molecule_name)
    
    def _extract_dev_codes(self, synonyms: List[str]) -> List[str]:
        """Extract development codes (e.g., ODM-201, ARN-509)"""
        import re
        dev_codes = []
        
        pattern = r'^[A-Z]{2,5}[-\s]?\d{3,7}[A-Z]?$'
        
        for syn in synonyms:
            syn = syn.strip()
            if re.match(pattern, syn, re.IGNORECASE):
                if syn not in dev_codes and len(dev_codes) < 20:
                    dev_codes.append(syn)
        
        return dev_codes
    
    def _extract_cas_number(self, synonyms: List[str]) -> str:
        """Extract CAS registry number"""
        import re
        pattern = r'^\d{2,7}-\d{2}-\d$'
        
        for syn in synonyms:
            if re.match(pattern, syn):
                return syn
        
        return None
    
    def _filter_synonyms(self, synonyms: List[str]) -> List[str]:
        """Filter and clean synonyms"""
        filtered = []
        
        for syn in synonyms:
            syn = syn.strip()
            
            # Skip if too short or too long
            if len(syn) < 3 or len(syn) > 100:
                continue
            
            # Skip if already in list
            if syn.lower() in [s.lower() for s in filtered]:
                continue
            
            # Skip CID numbers
            if syn.startswith("CID"):
                continue
            
            filtered.append(syn)
            
            if len(filtered) >= 50:
                break
        
        return filtered
    
    async def _get_molecular_formula(self, molecule_name: str) -> str:
        """Get molecular formula"""
        try:
            url = f"{self.base_url}/compound/name/{molecule_name}/property/MolecularFormula/JSON"
            
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    props = data.get("PropertyTable", {}).get("Properties", [])
                    if props:
                        return props[0].get("MolecularFormula", "")
        except:
            pass
        
        return ""
    
    async def _get_smiles(self, molecule_name: str) -> str:
        """Get SMILES notation"""
        try:
            url = f"{self.base_url}/compound/name/{molecule_name}/property/CanonicalSMILES/JSON"
            
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    props = data.get("PropertyTable", {}).get("Properties", [])
                    if props:
                        return props[0].get("CanonicalSMILES", "")
        except:
            pass
        
        return ""
    
    def _empty_result(self, molecule_name: str) -> PubChemData:
        """Return empty result"""
        return PubChemData(
            molecule_name=molecule_name,
            dev_codes=[],
            cas_number=None,
            synonyms=[],
            molecular_formula="",
            smiles=""
        )

# Global instance
pubchem_client = PubChemClient()
