#!/usr/bin/env python3
"""
Pharmyrus v4.0 - Test Script
Run this after deployment to validate all endpoints
"""
import requests
import json
import time
from typing import Dict, Any

# ============================================================================
# CONFIGURATION
# ============================================================================

# 🔧 CHANGE THIS to your deployed URL
BASE_URL = "https://pharmyrus-v4-production.up.railway.app"

# Test cases
TEST_CASES = {
    "wo_number": "WO2011051540",
    "patent_br": "BR112012008823B8",
    "patent_us": "US9376391B2",
    "molecule": "darolutamide"
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(title: str):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def print_result(success: bool, message: str, duration: float = None):
    """Print test result"""
    emoji = "✅" if success else "❌"
    dur_str = f" ({duration:.2f}s)" if duration else ""
    print(f"{emoji} {message}{dur_str}")

def test_endpoint(method: str, url: str, json_data: Dict = None, timeout: int = 30) -> Dict[str, Any]:
    """Test a single endpoint"""
    try:
        start = time.time()
        
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=timeout)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
        
        duration = time.time() - start
        
        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json(),
                "status_code": response.status_code,
                "duration": duration
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text,
                "duration": duration
            }
    
    except requests.exceptions.Timeout:
        return {"success": False, "error": f"Timeout after {timeout}s"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection failed - check if server is running"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_health():
    """Test health endpoint"""
    print_header("TEST 1: Health Check")
    
    url = f"{BASE_URL}/health"
    print(f"🔍 Testing: {url}")
    
    result = test_endpoint("GET", url, timeout=10)
    
    if result["success"]:
        data = result["data"]
        print_result(True, f"Server is healthy", result["duration"])
        print(f"   Version: {data.get('version', 'unknown')}")
        print(f"   Crawlers Ready: {data.get('crawlers_ready', 0)}/{data.get('crawler_pool_size', 0)}")
        print(f"   SerpAPI Keys: {data.get('serpapi_keys_available', 0)}")
        return True
    else:
        print_result(False, f"Health check failed: {result.get('error', 'Unknown error')}")
        return False

def test_wo_endpoint():
    """Test WO details endpoint"""
    print_header("TEST 2: WO Details (ALL Countries)")
    
    wo_number = TEST_CASES["wo_number"]
    url = f"{BASE_URL}/api/v1/wo/{wo_number}"
    print(f"🔍 Testing: {url}")
    print(f"   Expecting: 59 worldwide applications")
    
    result = test_endpoint("GET", url, timeout=30)
    
    if result["success"]:
        data = result["data"]
        total_apps = data.get("total_applications", 0)
        total_countries = data.get("total_countries", 0)
        
        print_result(True, f"WO details retrieved", result["duration"])
        print(f"   WO Number: {data.get('wo_number', '')}")
        print(f"   Title: {data.get('title', 'N/A')[:60]}...")
        print(f"   Assignee: {data.get('assignee', 'N/A')}")
        print(f"   Applications: {total_apps}")
        print(f"   Countries: {total_countries}")
        
        # Check if BR is present
        apps = data.get("worldwide_applications", {})
        br_found = False
        for year, year_apps in apps.items():
            for app in year_apps:
                if app.get("country_code") == "BR":
                    br_found = True
                    print(f"   ✅ BR found: {app.get('application_number', '')}")
                    break
            if br_found:
                break
        
        if total_apps >= 50:
            print_result(True, f"Found {total_apps} applications (expected ~59)")
        else:
            print_result(False, f"Only {total_apps} applications found (expected ~59)")
        
        return total_apps >= 50
    else:
        print_result(False, f"WO endpoint failed: {result.get('error', 'Unknown error')}")
        return False

def test_patent_endpoint():
    """Test patent details endpoint"""
    print_header("TEST 3: Patent Details (Google Patents + INPI)")
    
    # Test BR patent
    br_patent = TEST_CASES["patent_br"]
    url = f"{BASE_URL}/api/v1/patent/{br_patent}"
    print(f"🔍 Testing BR patent: {url}")
    
    result = test_endpoint("GET", url, timeout=20)
    
    if result["success"]:
        data = result["data"]
        
        print_result(True, f"Patent details retrieved", result["duration"])
        print(f"   Patent: {data.get('publication_number', '')}")
        print(f"   Country: {data.get('country_code', '')}")
        print(f"   Title: {data.get('title', 'N/A')[:60]}...")
        print(f"   Assignee: {data.get('assignee', 'N/A')}")
        
        # Check sources
        sources = data.get("sources", {})
        if "google_patents" in sources:
            print(f"   ✅ Google Patents data present")
        if "inpi" in sources:
            print(f"   ✅ INPI data present (enriched)")
        
        return True
    else:
        print_result(False, f"Patent endpoint failed: {result.get('error', 'Unknown error')}")
        return False

def test_search_endpoint():
    """Test search pipeline endpoint"""
    print_header("TEST 4: Search Pipeline (Complete)")
    
    url = f"{BASE_URL}/api/v1/search"
    payload = {
        "molecule_name": TEST_CASES["molecule"],
        "max_wos": 3,
        "include_inpi": True
    }
    
    print(f"🔍 Testing: POST {url}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    print(f"   ⚠️  This may take 2-5 minutes...")
    
    result = test_endpoint("POST", url, json_data=payload, timeout=300)
    
    if result["success"]:
        data = result["data"]
        summary = data.get("executive_summary", {})
        patents = data.get("patents", [])
        
        print_result(True, f"Search completed", result["duration"])
        print(f"   Molecule: {summary.get('molecule_name', '')}")
        print(f"   Total Patents: {summary.get('total_patents', 0)}")
        print(f"   Total Families: {summary.get('total_families', 0)}")
        print(f"   Patents Retrieved: {len(patents)}")
        
        # Check metadata
        metadata = data.get("search_metadata", {})
        print(f"   WOs Found: {metadata.get('wo_numbers_found', 0)}")
        print(f"   WOs Processed: {metadata.get('wo_numbers_processed', 0)}")
        
        return True
    else:
        print_result(False, f"Search endpoint failed: {result.get('error', 'Unknown error')}")
        return False

def print_browser_urls():
    """Print URLs for browser testing"""
    print_header("🌐 BROWSER TEST URLS")
    
    print("Copy these URLs to test in your browser:\n")
    
    print("1. API Documentation (Swagger UI):")
    print(f"   {BASE_URL}/docs\n")
    
    print("2. Health Check:")
    print(f"   {BASE_URL}/health\n")
    
    print("3. WO Details:")
    print(f"   {BASE_URL}/api/v1/wo/{TEST_CASES['wo_number']}\n")
    
    print("4. Patent Details (BR):")
    print(f"   {BASE_URL}/api/v1/patent/{TEST_CASES['patent_br']}\n")
    
    print("5. Patent Details (US):")
    print(f"   {BASE_URL}/api/v1/patent/{TEST_CASES['patent_us']}\n")
    
    print("6. Search (use Swagger UI for POST):")
    print(f"   {BASE_URL}/docs#/default/search_molecule_api_v1_search_post")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all tests"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                   PHARMYRUS v4.0 - TEST SUITE                             ║
║                                                                           ║
║  This script validates all endpoints after deployment                    ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")
    
    print(f"📍 Base URL: {BASE_URL}")
    print(f"📋 Test Cases: {len(TEST_CASES)}")
    
    # Run tests
    results = []
    
    results.append(("Health Check", test_health()))
    time.sleep(1)
    
    results.append(("WO Endpoint", test_wo_endpoint()))
    time.sleep(1)
    
    results.append(("Patent Endpoint", test_patent_endpoint()))
    time.sleep(1)
    
    # Uncomment when endpoint 3 is ready
    # results.append(("Search Endpoint", test_search_endpoint()))
    
    # Summary
    print_header("📊 TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        emoji = "✅" if success else "❌"
        print(f"{emoji} {name}")
    
    print(f"\n🎯 Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Pharmyrus v4.0 is working correctly")
        print_browser_urls()
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("\n🔧 Check deployment logs and environment variables")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
