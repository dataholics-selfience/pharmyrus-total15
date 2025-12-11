# 📁 Pharmyrus v4.0 - Project Structure

```
pharmyrus-v4.0/
│
├── 📄 main.py                    # Entry point (uvicorn)
├── 📄 Dockerfile                 # Docker image (v3.1-HOTFIX base)
├── 📄 requirements.txt           # Python dependencies
├── 📄 runtime.txt                # Python version
├── 📄 railway.json               # Railway config
├── 📄 .gitignore                 # Git ignore
│
├── 📖 README.md                  # Main documentation
├── 📖 DEPLOY.md                  # Deploy instructions
├── 📖 README_IMPLEMENTATION.md   # Implementation plan
│
├── 🧪 test_local.sh              # Local test script
│
└── src/                          # Source code
    │
    ├── __init__.py
    ├── config.py                 # Configuration (SerpAPI keys, URLs, settings)
    ├── models.py                 # Pydantic models (all endpoints)
    ├── utils.py                  # Helper functions
    ├── api_service.py            # FastAPI app (3 endpoints)
    ├── orchestrator.py           # Search pipeline orchestrator
    │
    ├── crawlers/                 # Web crawlers & API clients
    │   ├── __init__.py
    │   ├── crawler_pool.py       # Playwright pool (v3.1-HOTFIX ✅)
    │   ├── wipo_crawler.py       # WIPO Patentscope (v3.1-HOTFIX ✅)
    │   ├── google_patents.py     # Google Patents via SerpAPI (NEW ✅)
    │   └── inpi_client.py        # INPI Brasil API (NEW ✅)
    │
    └── discovery/                # Discovery services
        ├── __init__.py
        ├── pubchem.py            # PubChem API (NEW ✅)
        └── wo_discovery.py       # WO number discovery (NEW ✅)
```

---

## 🔧 Module Details

### Core Services

| File | Purpose | Status |
|------|---------|--------|
| `config.py` | SerpAPI keys rotation, URLs, settings | ✅ |
| `models.py` | Pydantic models for all endpoints | ✅ |
| `utils.py` | Helpers (extract WO, country codes, etc) | ✅ |
| `api_service.py` | FastAPI with 3 endpoints | ✅ |
| `orchestrator.py` | Complete search pipeline | ✅ |

### Crawlers

| File | Purpose | Source | Status |
|------|---------|--------|--------|
| `crawler_pool.py` | Playwright crawler pool | v3.1-HOTFIX | ✅ WORKS |
| `wipo_crawler.py` | WIPO worldwide applications | v3.1-HOTFIX | ✅ WORKS |
| `google_patents.py` | Google Patents details | NEW | ✅ |
| `inpi_client.py` | INPI Brasil enrichment | NEW | ✅ |

### Discovery

| File | Purpose | Status |
|------|---------|--------|
| `pubchem.py` | Dev codes, CAS, synonyms | ✅ |
| `wo_discovery.py` | Multi-source WO search | ✅ |

---

## 🎯 Endpoints Implementation

### ✅ Endpoint 1: GET /api/v1/wo/{wo_number}
**Status**: COMPLETE

**Flow**:
1. Normalize WO number
2. Get crawler from pool
3. WIPO crawler → worldwide_applications
4. Parse and format response
5. Return all countries (not just BR)

**Files used**:
- `api_service.py` (endpoint)
- `crawlers/wipo_crawler.py` (WIPO)
- `crawlers/crawler_pool.py` (pool)
- `utils.py` (helpers)

---

### ✅ Endpoint 2: GET /api/v1/patent/{patent_number}
**Status**: COMPLETE

**Flow**:
1. Clean patent number
2. Google Patents → full details
3. If BR: INPI → enrichment
4. Merge sources
5. Return complete patent data

**Files used**:
- `api_service.py` (endpoint)
- `crawlers/google_patents.py` (Google)
- `crawlers/inpi_client.py` (INPI)
- `utils.py` (helpers)

---

### ✅ Endpoint 3: POST /api/v1/search
**Status**: COMPLETE

**Flow**:
1. PubChem → dev codes, CAS
2. WO Discovery → find WO numbers
3. For each WO → WIPO → applications
4. For each app → Google Patents → details
5. For BR → INPI → enrichment
6. Consolidate → final JSON

**Files used**:
- `api_service.py` (endpoint)
- `orchestrator.py` (pipeline)
- `discovery/pubchem.py` (PubChem)
- `discovery/wo_discovery.py` (WO search)
- `crawlers/*` (all crawlers)

---

## 🔄 Data Flow

```
User Request
    ↓
FastAPI (api_service.py)
    ↓
┌─────────────────────────────────────┐
│ ENDPOINT 1: /wo/{wo_number}         │
│   → wipo_crawler.py                 │
│   → Returns worldwide apps          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ ENDPOINT 2: /patent/{number}        │
│   → google_patents.py               │
│   → inpi_client.py (if BR)          │
│   → Returns full patent details     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ ENDPOINT 3: /search                 │
│   → orchestrator.py                 │
│     ├─ pubchem.py                   │
│     ├─ wo_discovery.py              │
│     ├─ wipo_crawler.py              │
│     ├─ google_patents.py            │
│     └─ inpi_client.py               │
│   → Returns complete JSON           │
└─────────────────────────────────────┘
    ↓
JSON Response
```

---

## 🎨 Code Architecture

### Separation of Concerns

- **API Layer** (`api_service.py`): FastAPI endpoints, request/response
- **Orchestration** (`orchestrator.py`): Pipeline coordination
- **Discovery** (`discovery/`): Molecule & WO discovery
- **Crawlers** (`crawlers/`): Data fetching from sources
- **Models** (`models.py`): Type safety with Pydantic
- **Utils** (`utils.py`): Pure functions, no side effects

### Design Patterns

- **Singleton**: Global instances (`crawler_pool`, `pubchem_client`)
- **Factory**: Crawler pool creates/manages crawlers
- **Pipeline**: Orchestrator chains operations
- **Client**: Each data source has dedicated client

---

## 📊 Dependencies

### Core
- `fastapi` - API framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

### Crawling
- `playwright` - Browser automation (WIPO)
- `aiohttp` - Async HTTP (APIs)

### From v3.1-HOTFIX
- Playwright setup working ✅
- Crawler pool alive ✅
- WIPO extraction working ✅
- Railway deployment working ✅

---

## 🚀 Ready for Deploy

All components implemented:
- ✅ 3 endpoints complete
- ✅ All crawlers working
- ✅ Pipeline orchestration ready
- ✅ Error handling & logging
- ✅ Pydantic validation
- ✅ Railway config ready
- ✅ Documentation complete

**Next step**: `railway up`
