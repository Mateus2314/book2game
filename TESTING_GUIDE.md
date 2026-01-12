# 🚀 Guia de Testes - Book2Game

## Passo 1: Iniciar os Serviços Docker

```powershell
# No diretório raiz do projeto
docker-compose up -d
```

**Aguarde ~30 segundos** para todos os serviços iniciarem. Verifique o status:

```powershell
docker-compose ps
```

✅ Esperado: Todos os serviços com status `Up` (healthy):
- `book2game_postgres` - Porta 5432
- `book2game_redis` - Porta 6379  
- `book2game_redis_commander` - Porta 8081
- `book2game_backend` - Porta 8000

---

## Passo 2: Executar Migrations do Banco

```powershell
# Criar as tabelas do banco de dados
docker-compose exec backend alembic upgrade head
```

✅ Se houver erro "no such file", primeiro crie a migration:

```powershell
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"
docker-compose exec backend alembic upgrade head
```

---

## Passo 3: Verificar Logs

```powershell
# Ver logs do backend (Ctrl+C para sair)
docker-compose logs -f backend

# Verificar se há erros
docker-compose logs backend | Select-String -Pattern "ERROR"
```

✅ Esperado: Logs estruturados JSON com `request_id`, sem erros de conexão

---

## Passo 4: Testar API Health Check

```powershell
# Health check
curl http://localhost:8000/health

# Ou no navegador:
# http://localhost:8000
```

✅ Esperado: `{"status": "healthy"}`

---

## Passo 5: Acessar Documentação Interativa (Swagger)

Abra no navegador:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

✅ Você verá todos os endpoints disponíveis:
- `/api/v1/auth/register` - Registrar usuário
- `/api/v1/auth/login` - Login
- `/api/v1/auth/refresh-token` - Refresh token

---

## Passo 6: Visualizar Redis Cache

Abra no navegador:
- **Redis Commander**: http://localhost:8081

✅ Interface web para ver:
- Keys de cache
- TTLs
- Valores armazenados

---

## Passo 7: Executar Testes Automatizados

```powershell
# Todos os testes com coverage
docker-compose exec backend pytest -v

# Com relatório de coverage
docker-compose exec backend pytest -v --cov=app --cov-report=term-missing

# Apenas testes unitários
docker-compose exec backend pytest tests/unit/ -v -m unit

# Apenas testes de integração
docker-compose exec backend pytest tests/integration/ -v -m integration

# Verificar coverage mínimo (80%)
docker-compose exec backend pytest --cov=app --cov-fail-under=80
```

✅ Esperado: **Coverage ≥80%**, todos testes passando

---

## Passo 8: Testar Endpoints Manualmente

### 8.1 Registrar um usuário

```powershell
# PowerShell
$body = @{
    email = "teste@exemplo.com"
    password = "senha123456"
    full_name = "Usuario Teste"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

✅ Esperado: `201 Created` com dados do usuário (sem `hashed_password`)

### 8.2 Fazer Login

```powershell
# PowerShell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login?email=teste@exemplo.com&password=senha123456" `
    -Method POST

$token = $response.access_token
Write-Host "Token obtido: $token"
```

✅ Esperado: `access_token`, `refresh_token`, `token_type: bearer`

### 8.3 Verificar Rate Limiting

```powershell
# Tente registrar 6 vezes seguidas (limite é 5/min)
1..6 | ForEach-Object {
    try {
        $body = @{
            email = "teste$_@exemplo.com"
            password = "senha123"
        } | ConvertTo-Json
        
        $result = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
            -Method POST `
            -ContentType "application/json" `
            -Body $body
        Write-Host "[$_] Sucesso: $($result.email)"
    } catch {
        Write-Host "[$_] RATE LIMITED (esperado na 6ª tentativa)" -ForegroundColor Yellow
    }
}
```

✅ Esperado: 6ª tentativa retorna `429 Too Many Requests`

---

## Passo 9: Verificar Métricas

```powershell
curl http://localhost:8000/metrics
```

✅ Esperado: Estatísticas da aplicação:
- `requests_total`
- `avg_response_time_ms`
- `cache_hit_rate`

---

## Passo 10: Verificar Conexões

```powershell
# PostgreSQL
docker-compose exec postgres psql -U book2game -d book2game_db -c "\dt"

# Redis
docker-compose exec redis redis-cli ping
docker-compose exec redis redis-cli KEYS "*"

# Verificar cache hit/miss
docker-compose exec redis redis-cli INFO stats | Select-String -Pattern "keyspace"
```

---

## 🎯 Checklist Completo

- [ ] Docker Compose subiu (4 containers)
- [ ] Migrations executadas com sucesso
- [ ] Health check retorna `healthy`
- [ ] Swagger acessível em `/docs`
- [ ] Redis Commander acessível (porta 8081)
- [ ] Testes automatizados passando (≥80% coverage)
- [ ] Registro de usuário funcionando
- [ ] Login retorna tokens JWT
- [ ] Rate limiting bloqueando após 5 tentativas
- [ ] Métricas disponíveis
- [ ] PostgreSQL conectado
- [ ] Redis funcionando

---

## 🐛 Troubleshooting

### Erro: "port is already allocated"
```powershell
# Parar containers conflitantes
docker-compose down
netstat -ano | findstr :8000  # Ver processo usando porta
# Matar processo ou mudar porta no docker-compose.yml
```

### Erro: "Connection refused" Redis/PostgreSQL
```powershell
# Recriar volumes
docker-compose down -v
docker-compose up -d
```

### Erro: Testes falhando
```powershell
# Ver logs detalhados
docker-compose exec backend pytest -vv --tb=short

# Limpar cache de testes
docker-compose exec backend pytest --cache-clear
```

### Ver logs em tempo real
```powershell
# Backend
docker-compose logs -f backend

# Todos os serviços
docker-compose logs -f
```

---

## 📊 Próximos Passos (APIs Externas)

Quando chegar no **Step 8** (REST API completa), você poderá testar:

```powershell
# Buscar livro (requer Google Books API key)
curl "http://localhost:8000/api/v1/books/search?q=Harry+Potter"

# Gerar recomendação (requer todas as APIs)
$headers = @{ Authorization = "Bearer $token" }
$body = @{ book_id = "google_books_id_aqui" } | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/recommendations" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $body
```

---

## 🔗 Links Rápidos

- API Docs: http://localhost:8000/docs
- Redis Commander: http://localhost:8081
- Health Check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

---

**🎉 Pronto para testar!** Comece pelo **Passo 1** e siga em ordem.
