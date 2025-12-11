# 🚀 PHARMYRUS v4.0 - IMPLEMENTAÇÃO

## ORDEM DE DESENVOLVIMENTO

### FASE 1: Endpoint WO Completo ✅ (PRIMEIRO)
**GET /api/v1/wo/{wo_number}**

Objetivo: Retornar TODAS as aplicações mundiais do WO (não só BR)

Exemplo: `/api/v1/wo/WO2011051540`
```json
{
  "wo_number": "WO2011051540",
  "title": "Compounds for treating cancer...",
  "abstract": "...",
  "assignee": "Orion Corporation",
  "filing_date": "2010-10-27",
  "publication_date": "2011-05-05",
  
  "worldwide_applications": {
    "total_countries": 59,
    "applications": [
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
      },
      // ... todas as 59 aplicações
    ]
  }
}
```

Base: v3.1-HOTFIX já extrai isso via WIPO Crawler (Playwright)

---

### FASE 2: Endpoint Patent Completo ✅ (SEGUNDO)
**GET /api/v1/patent/{patent_number}**

Objetivo: Retornar TODOS os dados de UMA patente específica

Exemplo: `/api/v1/patent/BR112012008823B8`
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
  "inventors": ["Inventor 1", "Inventor 2"],
  
  "legal_status": "Active",
  "legal_status_detail": "Patent Granted",
  
  "family_id": "43569448",
  "wo_number": "WO2011051540",
  
  "sources": {
    "google_patents": {
      "url": "https://patents.google.com/patent/BR112012008823B8",
      "pdf_url": "...",
      "cpc_classifications": ["C07D", "A61K"],
      "ipc_classifications": ["C07D401/04"]
    },
    "inpi": {
      "status": "Concedido",
      "process_number": "1120120088237",
      "events": [...]
    }
  }
}
```

Fontes:
- Google Patents (SerpAPI engine=google_patents_details)
- INPI API (se BR)

---

### FASE 3: Endpoint Search Completo ✅ (TERCEIRO)
**POST /api/v1/search**

Objetivo: Pipeline completo Opção A → JSON igual target-buscas.json

Request:
```json
{
  "molecule_name": "darolutamide",
  "max_wos": 10,
  "include_inpi": true
}
```

Response (formato target-buscas.json):
```json
{
  "executive_summary": {
    "molecule_name": "darolutamide",
    "total_patents": 118,
    "total_families": 65,
    "jurisdictions": {"brazil": 13, "usa": 55, ...},
    "search_duration_seconds": 450.5
  },
  "patents": [
    {
      "publication_number": "BR112012008823B8",
      "title": "...",
      "abstract": "...",
      // ... todos os campos
    }
  ],
  "search_metadata": {
    "sources_used": ["PubChem", "Google Patents", "WIPO", "INPI"],
    "wo_numbers_found": 15,
    "wo_numbers_processed": 10
  }
}
```

Pipeline:
1. PubChem → dev_codes, cas, synonyms
2. WO Discovery (Google + SerpAPI) → wo_numbers
3. Para cada WO: WIPO Crawler → worldwide_applications
4. Para cada aplicação: Google Patents → detalhes completos
5. Para cada BR: INPI → enrichment
6. Consolidação → JSON final

---

## ESTRUTURA DE CÓDIGO

```
src/
├── __init__.py
├── config.py              # 9 chaves SerpAPI + URLs
├── models.py              # Pydantic models
│
├── crawlers/
│   ├── __init__.py
│   ├── crawler_pool.py    # v3.1-HOTFIX (funciona)
│   ├── wipo_crawler.py    # v3.1-HOTFIX (melhorado)
│   ├── google_patents.py  # NOVO - SerpAPI details
│   └── inpi_client.py     # NOVO - INPI API
│
├── discovery/
│   ├── __init__.py
│   ├── pubchem.py         # NOVO - PubChem synonyms
│   └── wo_discovery.py    # NOVO - Multi-source WO search
│
├── orchestrator.py        # NOVO - Pipeline completo
├── api_service.py         # FastAPI endpoints
└── utils.py               # Helpers

main.py
requirements.txt
Dockerfile                 # v3.1-HOTFIX (funciona)
```

---

## CHECKLIST DE IMPLEMENTAÇÃO

### Endpoint 1 (WO Completo):
- [ ] Copiar wipo_crawler.py do v3.1-HOTFIX
- [ ] Copiar crawler_pool.py do v3.1-HOTFIX
- [ ] Criar endpoint GET /api/v1/wo/{wo_number}
- [ ] Testar localmente com WO2011051540
- [ ] Validar: 59 aplicações mundiais (não só BR)

### Endpoint 2 (Patent Completo):
- [ ] Implementar google_patents.py (SerpAPI details)
- [ ] Implementar inpi_client.py (API existente)
- [ ] Criar endpoint GET /api/v1/patent/{patent_number}
- [ ] Testar com BR112012008823B8
- [ ] Validar: title, abstract, claims, dates, assignee

### Endpoint 3 (Search Completo):
- [ ] Implementar pubchem.py
- [ ] Implementar wo_discovery.py
- [ ] Implementar orchestrator.py (pipeline)
- [ ] Criar endpoint POST /api/v1/search
- [ ] Testar com darolutamide
- [ ] Validar: JSON igual target-buscas.json

### Deploy Railway:
- [ ] Copiar Dockerfile do v3.1-HOTFIX
- [ ] Configurar variáveis de ambiente
- [ ] Deploy e teste
- [ ] URLs para teste no browser

---

## PRÓXIMO PASSO IMEDIATO

Começar implementação do Endpoint 1 (WO Completo)
usando base v3.1-HOTFIX que já funciona
