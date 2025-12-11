# 📖 GUIA: Como Usar o Endpoint de Search

## 🎯 URL Base

```
https://pharmyrus-total14-production.up.railway.app
```

---

## 🔍 Endpoint: POST /api/v1/search

**Método:** POST (NÃO é GET!)  
**Path:** `/api/v1/search`  
**Content-Type:** `application/json`

---

## 📝 Request Body

### Estrutura:
```json
{
  "molecule_name": "string",
  "max_wos": 5,
  "country": "BR",
  "include_inpi": true
}
```

### Campos:

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|-------|------|-------------|--------|-----------|
| `molecule_name` | string | ✅ Sim | - | Nome da molécula (ex: "darolutamide") |
| `max_wos` | int | ❌ Não | 5 | Máximo de WO numbers para processar (1-20) |
| `country` | string | ❌ Não | null | Filtro de país (ex: "BR", "US", "EP") |
| `include_inpi` | bool | ❌ Não | true | Incluir dados do INPI Brasil |

---

## 🌐 Como Usar

### 1️⃣ Via Swagger UI (MAIS FÁCIL!)

1. Acessar: https://pharmyrus-total14-production.up.railway.app/docs

2. Clicar no endpoint **POST /api/v1/search**

3. Clicar em **"Try it out"**

4. Editar o JSON no Request body:
   ```json
   {
     "molecule_name": "darolutamide",
     "max_wos": 2
   }
   ```

5. Clicar em **"Execute"**

6. Ver resposta abaixo (aguardar 30-60 segundos)

---

### 2️⃣ Via cURL

```bash
curl -X POST "https://pharmyrus-total14-production.up.railway.app/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "molecule_name": "darolutamide",
    "max_wos": 2
  }'
```

**Com todos os parâmetros:**
```bash
curl -X POST "https://pharmyrus-total14-production.up.railway.app/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "molecule_name": "darolutamide",
    "max_wos": 3,
    "country": "BR",
    "include_inpi": true
  }'
```

---

### 3️⃣ Via Python

```python
import requests

url = "https://pharmyrus-total14-production.up.railway.app/api/v1/search"

payload = {
    "molecule_name": "darolutamide",
    "max_wos": 2,
    "country": "BR",
    "include_inpi": True
}

response = requests.post(url, json=payload)
print(response.json())
```

---

### 4️⃣ Via JavaScript/Node.js

```javascript
const url = "https://pharmyrus-total14-production.up.railway.app/api/v1/search";

const payload = {
  molecule_name: "darolutamide",
  max_wos: 2,
  country: "BR",
  include_inpi: true
};

fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 📊 Response Structure

```json
{
  "molecule_name": "darolutamide",
  "pubchem_data": {
    "cid": 12345,
    "dev_codes": ["ODM-201"],
    "cas_number": "1297538-32-9",
    "synonyms": ["..."]
  },
  "wo_discovery": {
    "wo_numbers": ["WO2011051540", "WO2016..."],
    "total_found": 2,
    "sources_used": ["google_patents", "google_search"]
  },
  "executive_summary": {
    "total_patents": 42,
    "jurisdictions": 15,
    "earliest_filing": "2011-01-15",
    "latest_filing": "2023-08-20",
    "patent_families": 8
  },
  "patents": [
    {
      "publication_number": "BR112012008823B1",
      "country_code": "BR",
      "title": "...",
      "assignee": "...",
      "filing_date": "2011-01-15",
      "wo_number": "WO2011051540",
      "sources": {...}
    }
  ],
  "search_metadata": {
    "duration_seconds": 45.2,
    "timestamp": "2025-12-11T18:50:00Z",
    "max_wos_requested": 2,
    "country_filter": "BR"
  }
}
```

---

## ⏱️ Tempo de Resposta

| max_wos | Tempo Estimado | Descrição |
|---------|----------------|-----------|
| 1 | 15-25s | Mais rápido |
| 2 | 25-40s | Recomendado para testes |
| 5 | 60-120s | Padrão |
| 10 | 120-240s | Demorado |
| 20 | 240-480s | Máximo (use com cautela) |

**Recomendação:** Começar com `max_wos: 2` para testes.

---

## ❌ Erros Comuns

### 1. Erro 404
```
GET /api/v1/search/darolutamide
```
**Problema:** Tentou usar GET com path parameter  
**Solução:** Usar POST com JSON body

### 2. Erro 422
```json
{"detail": [{"loc": ["body", "molecule_name"], "msg": "field required"}]}
```
**Problema:** Faltou `molecule_name` no body  
**Solução:** Adicionar campo obrigatório

### 3. Erro 500
```json
{"detail": "Internal error: ..."}
```
**Problema:** Erro no servidor  
**Solução:** Ver logs do Railway

### 4. Timeout (sem resposta)
**Problema:** `max_wos` muito alto (ex: 20)  
**Solução:** Reduzir para 2-5

---

## 🧪 Exemplos de Testes

### Teste 1: Busca Simples
```json
{
  "molecule_name": "aspirin"
}
```

### Teste 2: Busca Limitada
```json
{
  "molecule_name": "darolutamide",
  "max_wos": 2
}
```

### Teste 3: Busca com Filtro BR
```json
{
  "molecule_name": "niraparib",
  "max_wos": 3,
  "country": "BR",
  "include_inpi": true
}
```

### Teste 4: Busca Internacional
```json
{
  "molecule_name": "olaparib",
  "max_wos": 5,
  "country": null,
  "include_inpi": false
}
```

---

## 🎯 Resumo Rápido

1. **Método:** POST (não GET!)
2. **URL:** `/api/v1/search` (não `/api/v1/search/{molecule}`)
3. **Body:** JSON com `molecule_name` obrigatório
4. **Tempo:** 30-60s (depende de max_wos)
5. **Teste:** Use `/docs` (Swagger UI) primeiro!

---

## 📚 Links Úteis

- **Swagger UI:** https://pharmyrus-total14-production.up.railway.app/docs
- **Health Check:** https://pharmyrus-total14-production.up.railway.app/health
- **Exemplo WO:** https://pharmyrus-total14-production.up.railway.app/api/v1/wo/WO2011051540

---

✅ **USE O SWAGGER UI - É MAIS FÁCIL!**

https://pharmyrus-total14-production.up.railway.app/docs
