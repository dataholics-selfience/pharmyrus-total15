# 🚀 Pharmyrus v4.0 - Deploy Guide

## 📋 Checklist Pré-Deploy

- [ ] SerpAPI keys configuradas (9 keys)
- [ ] Railway CLI instalado
- [ ] Código testado localmente
- [ ] Dockerfile validado
- [ ] requirements.txt atualizado

---

## 🏠 Local Development

### 1. Instalar Dependências

```bash
cd /tmp/pharmyrus-v4.0

# Criar virtual environment (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Instalar Playwright browsers
playwright install chromium
```

### 2. Rodar Local

```bash
# Iniciar servidor
python main.py
```

Server disponível em: **http://localhost:8000**

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 3. Testar Endpoints

```bash
# Dar permissão de execução
chmod +x test_local.sh

# Rodar testes
./test_local.sh
```

**Testes manuais no browser:**

```
http://localhost:8000/health
http://localhost:8000/api/v1/wo/WO2011051540
http://localhost:8000/api/v1/patent/BR112012008823B8
```

---

## ☁️ Deploy Railway

### Opção 1: Railway CLI (Recomendado)

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Criar novo projeto (primeira vez)
railway init

# Deploy
railway up

# Ver logs
railway logs

# Ver URL
railway status
```

### Opção 2: Railway Web Interface

1. Acesse https://railway.app
2. Crie novo projeto: **"New Project" → "Deploy from GitHub"**
3. Conecte seu repositório
4. Railway detecta Dockerfile automaticamente
5. Configure variáveis de ambiente (ver abaixo)
6. Deploy automático

### Opção 3: GitHub Integration

1. Push código para GitHub
2. Conecte Railway ao repositório
3. Deploy automático em cada push

---

## 🔧 Variáveis de Ambiente (Railway)

Configure no Railway Dashboard → Variables:

```bash
# Required
PORT=8000

# SerpAPI Keys (9 keys for rotation)
SERPAPI_KEY_1=bc20bca64032a7ac59abf330bbdeca80aa79cd72bb208059056b10fb6e33e4bc
SERPAPI_KEY_2=3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d
# ... adicionar outras 7 keys

# INPI API (opcional - já tem default)
INPI_API_URL=https://crawler3-production.up.railway.app/api/data/inpi/patents

# Crawler Settings (opcional)
CRAWLER_POOL_SIZE=2
CRAWLER_TIMEOUT=60000
CRAWLER_MAX_RETRIES=3

# Rate Limiting (opcional)
DELAY_BETWEEN_WOS=2.0
DELAY_BETWEEN_QUERIES=1.0

# Logging (opcional)
LOG_LEVEL=INFO
```

---

## 🧪 Testar Deploy

Após deploy bem-sucedido, Railway fornece uma URL pública.

Exemplo: `https://pharmyrus-v4-production.up.railway.app`

### Testar Endpoints:

**1. Health Check**
```bash
curl https://seu-app.up.railway.app/health
```

**2. WO Endpoint**
```bash
curl https://seu-app.up.railway.app/api/v1/wo/WO2011051540
```

**3. Patent Endpoint**
```bash
curl https://seu-app.up.railway.app/api/v1/patent/BR112012008823B8
```

**4. Search Endpoint**
```bash
curl -X POST https://seu-app.up.railway.app/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"molecule_name":"darolutamide","max_wos":2,"include_inpi":false}'
```

### Testar no Browser:

```
https://seu-app.up.railway.app/docs
https://seu-app.up.railway.app/health
https://seu-app.up.railway.app/api/v1/wo/WO2011051540
```

---

## 📊 Monitoramento

### Railway Dashboard

- **Logs**: Railway → Deployments → Logs
- **Métricas**: CPU, RAM, Network
- **Health checks**: Status do /health endpoint

### Logs úteis para debugging:

```bash
# Seguir logs em tempo real
railway logs --follow

# Ver últimos 100 logs
railway logs --lines 100
```

**Buscar por:**
- `✅` = Sucesso
- `⚠️` = Warning
- `❌` = Erro
- `🔍` = Requests
- `📊` = Statistics

---

## 🐛 Troubleshooting

### Problema: Deploy falhou

**Solução:**
```bash
# Ver logs de build
railway logs --deployment

# Verificar Dockerfile
docker build -t pharmyrus-v4-test .
docker run -p 8000:8000 pharmyrus-v4-test
```

### Problema: Playwright não instalou

**Causa**: Dockerfile não instalou chromium

**Solução**: Verificar Dockerfile tem:
```dockerfile
RUN playwright install chromium
RUN playwright install-deps chromium
```

### Problema: Health check failing

**Causa**: Crawlers demorando para inicializar

**Solução**: 
- Aumentar `healthcheckTimeout` em railway.json
- Verificar logs: `railway logs`

### Problema: Timeout nos requests

**Causa**: WO com muitas aplicações (100+)

**Solução**:
- Limitar `max_wos` no request
- Implementar paginação futura

### Problema: SerpAPI rate limit

**Causa**: Muitas queries sem rotação

**Solução**:
- Verificar se todas 9 keys estão configuradas
- Verificar `DELAY_BETWEEN_QUERIES >= 1.0`

---

## 🔄 Atualizar Deploy

### Via Railway CLI:
```bash
# Commit mudanças
git add .
git commit -m "Update: feature X"

# Deploy nova versão
railway up
```

### Via GitHub:
- Push para branch configurada
- Railway faz deploy automático

---

## 📈 Performance Tips

### 1. Otimizar Crawler Pool
```bash
# Aumentar crawlers (mais memória)
CRAWLER_POOL_SIZE=3
```

### 2. Ajustar Timeouts
```bash
# Reduzir timeout se Railway timeout frequente
CRAWLER_TIMEOUT=45000  # 45s
```

### 3. Limitar Results
```json
{
  "molecule_name": "darolutamide",
  "max_wos": 5,  // Menos WOs = mais rápido
  "include_inpi": false  // Skip INPI se não precisa
}
```

---

## ✅ Checklist Pós-Deploy

- [ ] Health check respondendo
- [ ] Endpoint WO funcionando (WO2011051540)
- [ ] Endpoint Patent funcionando (BR112012008823B8)
- [ ] Endpoint Search funcionando (darolutamide, max_wos=2)
- [ ] Logs sem erros críticos
- [ ] Performance aceitável (<60s para search simples)
- [ ] Documentação /docs acessível

---

## 📞 Support

Em caso de problemas:

1. Verificar logs: `railway logs --follow`
2. Testar localmente primeiro
3. Validar variáveis de ambiente
4. Verificar SerpAPI quota
5. Revisar TROUBLESHOOTING acima

---

## 🎯 URLs de Teste (Após Deploy)

Substituir `SEU-APP-URL` pela URL do Railway:

```
Health: https://SEU-APP-URL/health
Docs: https://SEU-APP-URL/docs
WO Test: https://SEU-APP-URL/api/v1/wo/WO2011051540
Patent Test: https://SEU-APP-URL/api/v1/patent/BR112012008823B8
```

**Exemplo POST (Search):**
```bash
curl -X POST https://SEU-APP-URL/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "molecule_name": "darolutamide",
    "max_wos": 3,
    "include_inpi": true
  }'
```

---

🚀 **Bom deploy!**
