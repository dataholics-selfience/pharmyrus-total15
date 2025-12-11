# 🌐 Pharmyrus v4.0 - URLs para Testar no Browser

## ⚙️ Após Deploy Railway

Railway vai gerar uma URL pública. Exemplo:
```
https://pharmyrus-v4-production.up.railway.app
```

---

## 📋 Lista de URLs para Testar

### 1️⃣ Health Check
```
https://SEU-APP-URL/health
```

**Retorno esperado:**
```json
{
  "status": "healthy",
  "version": "4.0.0",
  "crawlers_ready": 2,
  "crawler_pool_size": 2,
  "serpapi_keys_available": 9
}
```

---

### 2️⃣ Root / Documentação
```
https://SEU-APP-URL/
```

**Retorno**: Lista de endpoints disponíveis

**API Docs (Swagger UI):**
```
https://SEU-APP-URL/docs
```

---

### 3️⃣ Endpoint WO - TODAS as Aplicações Mundiais

**URL Exemplo 1** (Darolutamide):
```
https://SEU-APP-URL/api/v1/wo/WO2011051540
```

**Retorno esperado**: 
- 59 aplicações mundiais
- Agrupadas por ano
- Países: BR, US, EP, CN, JP, CA, AU, KR, etc.

**URL Exemplo 2** (Outro WO):
```
https://SEU-APP-URL/api/v1/wo/WO2016162604
```

---

### 4️⃣ Endpoint Patent - Detalhes Completos

**URL Exemplo 1** (BR - Brasil):
```
https://SEU-APP-URL/api/v1/patent/BR112012008823B8
```

**Retorno esperado**:
- Title, abstract, claims
- Dates (priority, filing, publication, grant)
- Assignee, inventors
- Legal status
- Google Patents + INPI data

**URL Exemplo 2** (US - Estados Unidos):
```
https://SEU-APP-URL/api/v1/patent/US9376391B2
```

**URL Exemplo 3** (EP - Europa):
```
https://SEU-APP-URL/api/v1/patent/EP2496562B1
```

---

### 5️⃣ Endpoint Search - Pipeline Completo

⚠️ **Nota**: Search é POST, precisa usar curl ou Postman

**Via curl**:
```bash
curl -X POST https://SEU-APP-URL/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "molecule_name": "darolutamide",
    "max_wos": 2,
    "include_inpi": false
  }'
```

**Via Swagger UI** (no browser):
```
https://SEU-APP-URL/docs
```
- Clique em "POST /api/v1/search"
- Clique em "Try it out"
- Cole o JSON:
```json
{
  "molecule_name": "darolutamide",
  "max_wos": 2,
  "include_inpi": false
}
```
- Clique em "Execute"

---

## 🧪 Teste Progressivo (Ordem Recomendada)

### Nível 1: Health & Docs
1. `/health` - Deve retornar OK
2. `/` - Deve listar endpoints
3. `/docs` - Deve abrir Swagger UI

### Nível 2: WO Endpoint (Rápido)
4. `/api/v1/wo/WO2011051540` - Deve retornar 59 aplicações em ~10-15s

### Nível 3: Patent Endpoint (Médio)
5. `/api/v1/patent/BR112012008823B8` - Deve retornar dados completos em ~5-10s
6. `/api/v1/patent/US9376391B2` - Teste com US patent

### Nível 4: Search Endpoint (Complexo)
7. POST `/api/v1/search` com `max_wos=2` - Deve completar em ~30-60s
8. POST `/api/v1/search` com `max_wos=5` - Teste com mais WOs

---

## 📊 Resultados Esperados

### WO Endpoint (WO2011051540)
```json
{
  "wo_number": "WO2011051540",
  "title": "Compounds for treating cancer and other indications",
  "worldwide_applications": {
    "2010": [
      {"country_code": "BR", "application_number": "BR112012008823", ...},
      {"country_code": "US", "application_number": "US13/504,155", ...},
      // ... 57 more
    ]
  },
  "total_applications": 59,
  "total_countries": 59,
  "search_duration_seconds": 12.5
}
```

### Patent Endpoint (BR112012008823B8)
```json
{
  "publication_number": "BR112012008823B8",
  "country_code": "BR",
  "title": "Compounds for treating cancer...",
  "abstract": "The present invention relates...",
  "claims": "1. A compound of formula I...",
  "assignee": "Orion Corporation",
  "filing_date": "2010-10-27",
  "grant_date": "2019-03-26",
  "sources": {
    "google_patents": {...},
    "inpi": {...}
  }
}
```

### Search Endpoint (darolutamide, max_wos=2)
```json
{
  "executive_summary": {
    "molecule_name": "darolutamide",
    "total_patents": 25,
    "total_families": 8,
    "jurisdictions": {"BR": 3, "US": 10, "EP": 5, ...},
    "search_duration_seconds": 45.2
  },
  "patents": [
    {
      "publication_number": "BR112012008823B8",
      "title": "...",
      // ... full patent data
    },
    // ... 24 more patents
  ],
  "search_metadata": {
    "sources_used": ["PubChem", "Google Patents", "WIPO", "INPI"],
    "wo_numbers_found": 8,
    "wo_numbers_processed": 2
  }
}
```

---

## 🎨 Testando no Browser (Chrome DevTools)

### 1. Abra Chrome DevTools (F12)

### 2. Vá para Console

### 3. Cole este código para testar Search:

```javascript
fetch('https://SEU-APP-URL/api/v1/search', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    molecule_name: 'darolutamide',
    max_wos: 2,
    include_inpi: false
  })
})
.then(r => r.json())
.then(data => console.log(data))
```

---

## 📱 Testando no Postman

### Importar Collection:

```json
{
  "info": {"name": "Pharmyrus v4.0"},
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "https://SEU-APP-URL/health"
      }
    },
    {
      "name": "WO Details",
      "request": {
        "method": "GET",
        "url": "https://SEU-APP-URL/api/v1/wo/WO2011051540"
      }
    },
    {
      "name": "Patent Details",
      "request": {
        "method": "GET",
        "url": "https://SEU-APP-URL/api/v1/patent/BR112012008823B8"
      }
    },
    {
      "name": "Search",
      "request": {
        "method": "POST",
        "url": "https://SEU-APP-URL/api/v1/search",
        "body": {
          "mode": "raw",
          "raw": "{\"molecule_name\":\"darolutamide\",\"max_wos\":2}"
        }
      }
    }
  ]
}
```

---

## ✅ Checklist de Testes

### Browser (Direto na URL)
- [ ] `/health` - Status healthy
- [ ] `/docs` - Swagger UI carrega
- [ ] `/api/v1/wo/WO2011051540` - Retorna JSON com 59 apps
- [ ] `/api/v1/patent/BR112012008823B8` - Retorna patent completo

### Swagger UI (No browser, em /docs)
- [ ] GET `/api/v1/wo/{wo_number}` - Testa com WO2011051540
- [ ] GET `/api/v1/patent/{patent_number}` - Testa com BR112012008823B8
- [ ] POST `/api/v1/search` - Testa com darolutamide, max_wos=2

### Via curl (Terminal)
- [ ] Todos os 4 testes do QUICKSTART.md

---

## 🚨 Troubleshooting Visual

### ✅ SUCESSO - Health Check
```json
{"status": "healthy", "crawlers_ready": 2}
```

### ❌ ERRO - Crawlers não prontos
```json
{"status": "unhealthy", "crawlers_ready": 0}
```
**Solução**: Aguardar 1-2 minutos (Playwright inicializando)

### ⚠️ WARNING - Timeout
```
504 Gateway Timeout
```
**Solução**: Reduzir `max_wos` no request

---

🎯 **Todas as URLs prontas para testar!**

Após deploy, substitua `SEU-APP-URL` pela URL real do Railway.
