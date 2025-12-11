# HOTFIX3: Google Patents Playwright Crawler

## Problema
- SerpAPI retornando 429 (rate limit) para Google Patents
- Patent endpoint retornando dados vazios
- WIPO crawler acessando mas extraindo 0 dados

## Solução Implementada

### 1. Google Patents Direct Crawler (Playwright)
**Novo arquivo:** `src/crawlers/google_patents_playwright.py`

- Crawler direto do Google Patents (sem SerpAPI)
- Extração via Playwright (igual WIPO que funcionou bem)
- **SEM rate limits** (acesso direto ao HTML)
- Extrai:
  - Informações básicas (title, abstract, assignee, inventors, dates)
  - Classifications (CPC, IPC)
  - Legal status
  - **Patent family completo** (worldwide applications)
  - PDF URL

### 2. Pool Manager
**Novo arquivo:** `src/crawlers/google_patents_pool.py`

- Gerencia 2 crawlers Playwright para Google Patents
- Round-robin para distribuir carga
- Inicialização/shutdown coordenado

### 3. Integração no API Service
**Modificado:** `src/api_service.py`

Estratégia em camadas para `/api/v1/patent/{id}`:
1. **Tenta Playwright primeiro** (direto, sem rate limits)
2. **Fallback para SerpAPI** se Playwright falhar
3. **Enriquece com INPI** se patente BR

## Arquivos Modificados

1. `src/crawlers/__init__.py` - Export do google_patents_pool
2. `src/api_service.py` - Imports e inicialização do pool + lógica dual-source
3. **NOVOS:**
   - `src/crawlers/google_patents_playwright.py` (356 linhas)
   - `src/crawlers/google_patents_pool.py` (84 linhas)

## Benefícios

✅ **Elimina 429 errors** - Não depende mais de SerpAPI para patent details
✅ **Mais dados** - Patent family completo extraído diretamente
✅ **Mais rápido** - Acesso direto sem API intermediária
✅ **Fallback** - Mantém SerpAPI como backup se Playwright falhar
✅ **Testado** - Padrão igual ao WIPO que funcionou perfeitamente

## Próximos Passos (WIPO)

O WIPO crawler ainda precisa ajuste (extrai 0 dados):
- Seletores da página mudaram
- Clica na aba mas não acha tabela
- Requererá debug em ambiente real para identificar novos seletores

## Deploy

```bash
tar -xzf pharmyrus-v4.0-HOTFIX3.tar.gz && cd pharmyrus-v4.0
railway up
```

Tempo estimado: 2-3 minutos
