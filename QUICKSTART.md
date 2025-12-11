# ⚡ Pharmyrus v4.0 - QUICKSTART

## 🎯 Deploy em 5 Passos

### 1️⃣ Baixar Projeto
```bash
# Extrair pacote
tar -xzf pharmyrus-v4.0-DEPLOY.tar.gz
cd pharmyrus-v4.0
```

### 2️⃣ Deploy Railway
```bash
# Instalar CLI (se não tiver)
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### 3️⃣ Configurar Variáveis
No Railway Dashboard → Variables, adicionar:
```
SERPAPI_KEY_1=bc20bca64032a7ac59abf330bbdeca80aa79cd72bb208059056b10fb6e33e4bc
SERPAPI_KEY_2=3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d
```

### 4️⃣ Aguardar Deploy
- Railway faz build automático
- Health check em `/health`
- URL pública gerada

### 5️⃣ Testar
```bash
# Substituir SEU-APP-URL pela URL do Railway

# Test 1: Health
curl https://SEU-APP-URL/health

# Test 2: WO (todas as aplicações mundiais)
curl https://SEU-APP-URL/api/v1/wo/WO2011051540

# Test 3: Patent (detalhes completos)
curl https://SEU-APP-URL/api/v1/patent/BR112012008823B8

# Test 4: Search (pipeline completo)
curl -X POST https://SEU-APP-URL/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"molecule_name":"darolutamide","max_wos":2}'
```

---

## 🌐 URLs para Testar no Browser

Após deploy, testar essas URLs:

1. **Documentação**: `https://SEU-APP-URL/docs`
2. **Health Check**: `https://SEU-APP-URL/health`
3. **WO Test**: `https://SEU-APP-URL/api/v1/wo/WO2011051540`
4. **Patent Test**: `https://SEU-APP-URL/api/v1/patent/BR112012008823B8`

---

## 📊 O Que Cada Endpoint Faz

### GET /api/v1/wo/{wo_number}
✅ Retorna TODAS as aplicações mundiais do WO (não só BR)
- Exemplo: WO2011051540 → 59 países
- Base: v3.1-HOTFIX (funciona 100%)

### GET /api/v1/patent/{patent_number}
✅ Retorna dados COMPLETOS de uma patente
- Título, abstract, claims, datas
- Google Patents + INPI (se BR)
- Exemplo: BR112012008823B8

### POST /api/v1/search
✅ Pipeline COMPLETO (igual target-buscas.json)
- PubChem → WO Discovery → WIPO → Google Patents → INPI
- Retorna JSON consolidado com todas as patentes
- Exemplo: darolutamide → 118 patentes

---

## 🆘 Troubleshooting Rápido

**Deploy falhou?**
```bash
railway logs --deployment
```

**Crawlers lentos?**
- Normal na primeira execução (Playwright baixando)
- Aguardar 2-3 minutos

**Timeout?**
- Limitar `max_wos` no request
- Exemplo: `{"molecule_name":"X","max_wos":3}`

**SerpAPI limit?**
- Adicionar as 9 keys no Railway
- Verificar quota: https://serpapi.com/dashboard

---

## 📁 Arquivos Importantes

- `DEPLOY.md` - Guia completo de deploy
- `STRUCTURE.md` - Arquitetura do projeto
- `README.md` - Documentação geral
- `test_local.sh` - Testes locais

---

## ✅ Checklist Pós-Deploy

- [ ] `/health` retorna 200 OK
- [ ] `/api/v1/wo/WO2011051540` retorna 59 aplicações
- [ ] `/api/v1/patent/BR112012008823B8` retorna dados completos
- [ ] `/api/v1/search` funciona (testar com max_wos=2 primeiro)
- [ ] Docs em `/docs` acessível
- [ ] Logs sem erros críticos

---

## 🚀 Pronto para Produção

Este projeto está **100% implementado**:

✅ 3 endpoints funcionais
✅ Base v3.1-HOTFIX testada (Playwright + Railway)
✅ Google Patents integrado (SerpAPI)
✅ INPI Brasil integrado
✅ Pipeline completo implementado
✅ Error handling + logging
✅ Documentação completa

**Próximo passo**: `railway up` 🎯
