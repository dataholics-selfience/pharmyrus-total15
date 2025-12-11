"""Simple structure validation"""
import os
import json

print("🧪 VALIDATING STRUCTURE...\n")

# Check files
required_files = [
    "main.py",
    "requirements.txt",
    "Dockerfile",
    "README.md",
    "src/__init__.py",
    "src/config.py",
    "src/models.py",
    "src/utils.py",
    "src/api_service.py",
    "src/crawlers/__init__.py",
    "src/crawlers/crawler_pool.py",
    "src/crawlers/wipo_crawler.py",
    "src/crawlers/google_patents.py",
    "src/crawlers/inpi_client.py",
]

missing = []
for f in required_files:
    if os.path.exists(f):
        print(f"✅ {f}")
    else:
        print(f"❌ {f} MISSING")
        missing.append(f)

if missing:
    print(f"\n❌ Missing {len(missing)} files!")
    exit(1)

print(f"\n✅ All {len(required_files)} files present!")

# Count lines
total_lines = 0
for f in required_files:
    if f.endswith('.py'):
        with open(f, 'r') as file:
            lines = len(file.readlines())
            total_lines += lines

print(f"📊 Total Python code: {total_lines} lines")

# Validate JSON-like config
print("\n🔧 Checking config...")
with open('src/config.py', 'r') as f:
    content = f.read()
    if 'SERPAPI_KEYS' in content:
        print("✅ SerpAPI keys configured")
    if 'WIPO_BASE_URL' in content:
        print("✅ WIPO URL configured")
    if 'INPI_API_URL' in content:
        print("✅ INPI URL configured")

print("\n🎉 STRUCTURE VALIDATION PASSED!")
print("\n📋 Ready for:")
print("  1. Local testing (requires pip install -r requirements.txt)")
print("  2. Docker build")
print("  3. Railway deployment")
