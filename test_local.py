"""Quick validation test"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🧪 Testing imports...")

try:
    from src import config
    print("✅ config.py imported")
    
    from src import models
    print("✅ models.py imported")
    
    from src import utils
    print("✅ utils.py imported")
    
    from src.crawlers import crawler_pool, google_patents_client, inpi_client
    print("✅ crawlers imported")
    
    # Test utils functions
    wo = utils.normalize_wo_number("WO 2011/051540")
    assert wo == "WO2011051540", f"WO normalize failed: {wo}"
    print(f"✅ WO normalize: {wo}")
    
    country = utils.extract_country_code("BR112012008823B8")
    assert country == "BR", f"Country extraction failed: {country}"
    print(f"✅ Country code: {country}")
    
    clean = utils.clean_patent_number("BR 11 2012 008823 B8")
    assert clean == "BR112012008823B8", f"Patent clean failed: {clean}"
    print(f"✅ Patent clean: {clean}")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("\n📋 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Install Playwright: playwright install chromium")
    print("3. Run server: python main.py")
    print("4. Test endpoints at http://localhost:8000/docs")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
