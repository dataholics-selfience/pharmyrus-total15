# 🚀 Pharmyrus v4.0 - Patent Intelligence API

Complete patent search and analysis system for pharmaceutical patents.

## 📋 Features

- ✅ **WO Details**: Get ALL worldwide applications from a WO number (not just BR)
- ✅ **Patent Details**: Get complete data for any patent (Google Patents + INPI if BR)
- 🚧 **Search Pipeline**: Complete molecule search (PubChem → WO Discovery → WIPO → enrichment)

## 🏗️ Architecture

```
Pharmyrus v4.0
├── Base: v3.1-HOTFIX (Playwright + Railway deployment working)
├── New: Google Patents integration via SerpAPI
├── New: INPI Brasil API integration
└── New: Complete search pipeline
```

## 🎯 Endpoints

### 1. GET /api/v1/wo/{wo_number}
Get complete WO patent details with ALL worldwide applications.

**Example**: `/api/v1/wo/WO2011051540`

**Response**:
```json
{
  "wo_number": "WO2011051540",
  "title": "Compounds for treating cancer...",
  "worldwide_applications": {
    "2010": [
      {"country_code": "BR", "application_number": "BR112012008823", ...},
      {"country_code": "US", "application_number": "US13/504,155", ...}
    ]
  },
  "total_applications": 59,
  "total_countries": 59
}
```

### 2. GET /api/v1/patent/{patent_number}
Get complete details for a single patent.

**Example**: `/api/v1/patent/BR112012008823B8`

**Response**:
```json
{
  "publication_number": "BR112012008823B8",
  "country_code": "BR",
  "title": "Compounds for treating cancer...",
  "abstract": "...",
  "claims": "1. A compound of formula I...",
  "assignee": "Orion Corporation",
  "sources": {
    "google_patents": {...},
    "inpi": {...}
  }
}
```

### 3. POST /api/v1/search
Complete pipeline: molecule → WO discovery → details → enrichment.

**Request**:
```json
{
  "molecule_name": "darolutamide",
  "max_wos": 10,
  "include_inpi": true
}
```

**Response**: Format igual target-buscas.json (118 patentes)

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run server
python main.py
```

Server will be available at `http://localhost:8000`

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Docker

```bash
# Build
docker build -t pharmyrus-v4 .

# Run
docker run -p 8000:8000 pharmyrus-v4
```

### Railway Deploy

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

## 📊 Status

### ✅ Implemented (Working)
- Crawler Pool (Playwright, 2 crawlers)
- WIPO Crawler (worldwide applications extraction)
- Google Patents Client (SerpAPI integration)
- INPI Client (Brasil API integration)
- Endpoint 1: GET /api/v1/wo/{wo_number}
- Endpoint 2: GET /api/v1/patent/{patent_number}
- Health checks
- Logging & error handling
- Railway deployment ready

### 🚧 In Progress (Endpoint 3)
- PubChem integration
- WO Discovery (multi-source)
- Search Orchestrator
- Family consolidation
- Executive summary generation

### 📅 Future (v4.1)
- Patent type inference (Product/Process/etc)
- Therapeutic indication analysis
- Expiry date calculation
- Strategic notes generation
- EPO integration

## 🔧 Configuration

Environment variables:

```bash
# SerpAPI (9 keys for rotation)
SERPAPI_KEY_1=...
SERPAPI_KEY_2=...
# ... 9 keys total

# INPI API
INPI_API_URL=https://crawler3-production.up.railway.app/api/data/inpi/patents

# Crawler settings
CRAWLER_POOL_SIZE=2
CRAWLER_TIMEOUT=60000
CRAWLER_MAX_RETRIES=3

# Rate limiting
DELAY_BETWEEN_WOS=2.0
DELAY_BETWEEN_QUERIES=1.0
```

## 📝 Testing

```bash
# Test WO endpoint
curl http://localhost:8000/api/v1/wo/WO2011051540

# Test Patent endpoint
curl http://localhost:8000/api/v1/patent/BR112012008823B8

# Test Search endpoint
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"molecule_name": "darolutamide", "max_wos": 3}'
```

## 🏆 Credits

Built on top of v3.1-HOTFIX which successfully:
- ✅ Deployed to Railway with Playwright
- ✅ Extracted 59 worldwide applications from WO2011051540
- ✅ Maintained crawler pool alive
- ✅ Implemented retry logic with exponential backoff

## 📄 License

Proprietary - Genoi/Hypofarma
