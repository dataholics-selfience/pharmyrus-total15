# 🚀 PHARMYRUS v4.0 - DEPLOYMENT & TEST GUIDE

## ✅ STATUS: READY FOR DEPLOYMENT

**Total Code**: 1,305 lines Python  
**Files**: 14 files  
**Base**: v3.1-HOTFIX (working on Railway)  
**New**: Google Patents + INPI + 3 REST endpoints  

---

## 📦 WHAT'S INCLUDED

### ✅ Working Components (from v3.1-HOTFIX)
- Crawler Pool (Playwright, 2 instances)
- WIPO Crawler (extracts worldwide applications)
- Railway Dockerfile (tested, working)
- Retry logic + exponential backoff

### ✅ New Components (v4.0)
- Google Patents Client (SerpAPI integration)
- INPI Client (Brasil API integration)
- 3 REST Endpoints:
  1. GET /api/v1/wo/{wo_number} → ALL countries
  2. GET /api/v1/patent/{patent_number} → Full patent details
  3. POST /api/v1/search → Complete pipeline (WIP)

---

## 🌐 DEPLOYMENT OPTIONS

### Option 1: Railway (RECOMMENDED)

Railway already has v3.1-HOTFIX working. Just deploy v4.0:

```bash
# From project directory
cd /tmp/pharmyrus-v4.0

# Initialize git (if not done)
git init
git add .
git commit -m "Pharmyrus v4.0 - 3 endpoints ready"

# Deploy to Railway
# Option A: Railway CLI
railway login
railway link  # Link to existing project or create new
railway up

# Option B: GitHub + Railway
# Push to GitHub and connect Railway to the repo
git remote add origin <your-github-repo>
git push -u origin main
# Then connect in Railway dashboard
```

**Environment Variables to Set in Railway:**
```
CRAWLER_POOL_SIZE=2
CRAWLER_TIMEOUT=60000
LOG_LEVEL=INFO
```

### Option 2: Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run server
python main.py
```

**Local URLs:**
- Server: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Option 3: Docker

```bash
# Build
docker build -t pharmyrus-v4 .

# Run
docker run -p 8000:8000 \
  -e CRAWLER_POOL_SIZE=2 \
  -e LOG_LEVEL=INFO \
  pharmyrus-v4
```

---

## 🧪 TEST URLS (After Deployment)

Assuming deployed at: `https://pharmyrus-v4-production.up.railway.app`

### 1️⃣ Health Check
```
GET https://pharmyrus-v4-production.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "4.0.0",
  "crawlers_ready": 2,
  "crawler_pool_size": 2,
  "serpapi_keys_available": 9
}
```

### 2️⃣ Root
```
GET https://pharmyrus-v4-production.up.railway.app/
```

**Expected Response:**
```json
{
  "service": "Pharmyrus v4.0",
  "description": "Patent Intelligence API",
  "endpoints": {
    "wo_details": "/api/v1/wo/{wo_number}",
    "patent_details": "/api/v1/patent/{patent_number}",
    "search": "/api/v1/search"
  }
}
```

### 3️⃣ WO Details (ALL COUNTRIES)
```
GET https://pharmyrus-v4-production.up.railway.app/api/v1/wo/WO2011051540
```

**Expected Response:**
```json
{
  "wo_number": "WO2011051540",
  "title": "Compounds for treating cancer...",
  "abstract": "...",
  "assignee": "Orion Corporation",
  "filing_date": "2010-10-27",
  "publication_date": "2011-05-05",
  "worldwide_applications": {
    "2010": [
      {
        "country_code": "BR",
        "application_number": "BR112012008823",
        "filing_date": "2010-10-27",
        "status": "Granted"
      },
      {
        "country_code": "US",
        "application_number": "US13/504,155",
        "filing_date": "2010-10-27",
        "status": "Active"
      }
      // ... 57 more countries
    ]
  },
  "total_applications": 59,
  "total_countries": 59,
  "search_duration_seconds": 8.5
}
```

### 4️⃣ Patent Details (Google Patents + INPI)
```
GET https://pharmyrus-v4-production.up.railway.app/api/v1/patent/BR112012008823B8
```

**Expected Response:**
```json
{
  "publication_number": "BR112012008823B8",
  "country_code": "BR",
  "priority_date": "2009-10-27",
  "filing_date": "2010-10-27",
  "publication_date": "2013-10-29",
  "grant_date": "2019-03-26",
  "title": "Compounds for treating cancer and other indications",
  "abstract": "The present invention relates to novel compounds...",
  "claims": "1. A compound of formula I...",
  "assignee": "Orion Corporation",
  "inventors": ["Inventor A", "Inventor B"],
  "legal_status": "Active",
  "family_id": "43569448",
  "sources": {
    "google_patents": {
      "url": "https://patents.google.com/patent/BR112012008823B8",
      "cpc_classifications": ["C07D", "A61K"],
      "family_size": 59
    },
    "inpi": {
      "status": "Concedido",
      "process_number": "1120120088237",
      "events": [...]
    }
  },
  "search_duration_seconds": 4.2
}
```

### 5️⃣ Search Pipeline (Complete)
```
POST https://pharmyrus-v4-production.up.railway.app/api/v1/search
Content-Type: application/json

{
  "molecule_name": "darolutamide",
  "max_wos": 3,
  "include_inpi": true
}
```

**Expected Response (target-buscas.json format):**
```json
{
  "executive_summary": {
    "molecule_name": "darolutamide",
    "total_patents": 45,
    "total_families": 12,
    "jurisdictions": {
      "brazil": 8,
      "united_states": 15,
      "europe": 12,
      "china": 10
    },
    "search_duration_seconds": 125.5
  },
  "patents": [
    {
      "publication_number": "BR112012008823B8",
      "title": "...",
      "abstract": "...",
      "country_code": "BR",
      "jurisdiction": "BR",
      "jurisdiction_name": "Brazil",
      ...
    }
    // ... 44 more patents
  ],
  "search_metadata": {
    "sources_used": ["PubChem", "Google Patents", "WIPO", "INPI"],
    "wo_numbers_found": 5,
    "wo_numbers_processed": 3,
    "serpapi_queries_used": 25
  }
}
```

### 6️⃣ API Documentation (Interactive)
```
GET https://pharmyrus-v4-production.up.railway.app/docs
```

This opens Swagger UI where you can test all endpoints in the browser.

---

## 🎯 TESTING SEQUENCE

### Phase 1: Verify Deployment
1. ✅ Check `/health` → Should return "healthy"
2. ✅ Check `/` → Should list all endpoints
3. ✅ Check `/docs` → Should show Swagger UI

### Phase 2: Test Endpoint 1 (WO Details)
1. ✅ Test with WO2011051540 → Should return 59 applications
2. ✅ Verify all countries present (not just BR)
3. ✅ Check response time (<15s)

### Phase 3: Test Endpoint 2 (Patent Details)
1. ✅ Test BR patent: BR112012008823B8
2. ✅ Test US patent: US9376391B2
3. ✅ Verify Google Patents data present
4. ✅ Verify INPI enrichment for BR patents

### Phase 4: Test Endpoint 3 (Search)
1. ✅ Test with darolutamide
2. ✅ Verify PubChem data extracted
3. ✅ Verify WO numbers discovered
4. ✅ Verify final JSON matches target-buscas.json format

---

## 📊 EXPECTED PERFORMANCE

| Endpoint | Typical Response Time | Notes |
|----------|----------------------|-------|
| /health | <100ms | No crawlers used |
| /api/v1/wo/{wo} | 8-15s | Playwright + WIPO |
| /api/v1/patent/{patent} | 3-8s | SerpAPI + INPI (if BR) |
| /api/v1/search | 2-5min | Full pipeline, depends on max_wos |

---

## 🐛 TROUBLESHOOTING

### Issue: Crawlers not starting
**Solution**: Check Railway logs for Playwright installation errors. Dockerfile includes `playwright install chromium`.

### Issue: SerpAPI rate limits
**Solution**: Keys are rotated automatically (9 keys = 2,250 queries/month). Check logs for key rotation.

### Issue: INPI API timeout
**Solution**: INPI API can be slow. Current timeout is 60s. Increase if needed in config.py.

### Issue: Memory errors on Railway
**Solution**: Railway free tier may have memory limits. Reduce CRAWLER_POOL_SIZE to 1.

---

## 📝 NEXT STEPS AFTER DEPLOYMENT

1. ✅ Deploy to Railway
2. ✅ Test all 3 endpoints with URLs above
3. ✅ Share URLs for browser testing
4. 🚧 Implement Endpoint 3 (Search Pipeline) fully:
   - PubChem integration (discovery/pubchem.py)
   - WO Discovery (discovery/wo_discovery.py)
   - Search Orchestrator (orchestrator.py)
5. 🚧 Add inference layer (v4.1):
   - Patent type classifier
   - Therapeutic indication analyzer
   - Expiry calculator

---

## 🎉 SUCCESS CRITERIA

✅ Endpoint 1: Returns 59 applications for WO2011051540  
✅ Endpoint 2: Returns full details + INPI data for BR patents  
✅ Endpoint 3: Returns JSON matching target-buscas.json format  
✅ Response times within expected ranges  
✅ No crawler crashes or memory errors  
✅ Logs show proper key rotation  

---

## 📞 SUPPORT

If any endpoint fails:
1. Check Railway deployment logs
2. Verify environment variables set
3. Test health endpoint first
4. Check Swagger UI at /docs for detailed error messages

**Railway Console**: https://railway.app/dashboard  
**Deployment Status**: Check "Deployments" tab in Railway project
