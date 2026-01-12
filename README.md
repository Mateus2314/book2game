# Book2Game 📚🎮

Sistema de recomendação mobile-first que sugere jogos baseados em livros usando IA (Llama 3.1 8B Instruct).

## ✅ Status do Projeto

### 🚀 Implementado e Funcionando

#### Backend (FastAPI + Python 3.11)
- ✅ **Autenticação & Autorização**
  - Sistema JWT completo (access + refresh tokens)
  - Rate limiting (5/min auth, 60/min geral)
  - Validação de email e senha segura
  - CRUD completo de usuários

- ✅ **API de Recomendações**
  - Integração com Google Books API
  - Geração de jogos usando Llama 3.1 8B Instruct (Hugging Face)
  - Sistema de scoring baseado em similaridade
  - Mapeamento inteligente de gêneros literários para tags de jogos
  - Filtragem e validação de jogos gerados

- ✅ **Sistema de Cache (Redis)**
  - Cache automático de livros, jogos e recomendações
  - TTL configurável (padrão: 24h)
  - Graceful degradation (funciona sem Redis)
  - Hit rate tracking e estatísticas
  - Interface web (Redis Commander) para visualização

- ✅ **Banco de Dados (PostgreSQL)**
  - Models completos: User, Book, Game, Recommendation, UserBook
  - Migrations com Alembic
  - Relacionamentos e constraints
  - Índices otimizados

- ✅ **Testes Automatizados**
  - 49 testes unitários (100% passing)
  - Cobertura de serviços principais
  - Mocks completos de APIs externas
  - TDD rigoroso aplicado

- ✅ **DevOps & Infraestrutura**
  - Docker Compose completo
  - Conventional Commits configurado
  - Logging estruturado (Loguru + JSON)
  - Variáveis de ambiente com validação
  - CORS configurado

### 🔨 Em Desenvolvimento

#### Frontend
- ⏳ **Mobile (React Native + Expo)**
  - Estrutura básica criada
  - Integração com backend pendente
  - UI/UX em design

- ⏳ **Web (React + Vite)**
  - Boilerplate configurado
  - Interface administrativa pendente

### 📋 Próximas Features

#### Backend
- [ ] Testes de integração (E2E)
- [ ] Sistema de favoritos (UserBook completo)
- [ ] Histórico de recomendações
- [ ] Filtros avançados (gênero, rating, ano)
- [ ] Paginação de resultados
- [ ] Sistema de notificações por email
- [ ] Webhooks para eventos
- [ ] Métricas e analytics

#### Frontend Mobile
- [ ] Tela de login/registro
- [ ] Busca de livros com autocomplete
- [ ] Visualização de recomendações
- [ ] Sistema de favoritos
- [ ] Perfil do usuário
- [ ] Modo offline básico

#### Frontend Web
- [ ] Dashboard administrativo
- [ ] Visualização de estatísticas
- [ ] Gerenciamento de usuários
- [ ] Logs e monitoramento

#### DevOps
- [ ] CI/CD (GitHub Actions)
- [ ] Deploy automatizado (Railway/Render)
- [ ] Monitoramento (Sentry/Datadog)
- [ ] Testes de carga
- [ ] Backup automatizado

## 🎯 Funcionalidades Principais

## 🎯 Funcionalidades Principais

### Backend API
- 🔍 **Busca de livros** via Google Books API com cache inteligente
- 🤖 **Geração de jogos** usando Llama 3.1 8B Instruct (zero API RAWG/IGDB)
- ⚡ **Cache Redis** com TTL 24h e graceful degradation
- 🔐 **Autenticação JWT** segura com rate limiting
- 📊 **Scoring inteligente** baseado em similaridade de tags/gêneros
- 🧪 **Cobertura de testes** de 100% nos serviços principais

### Tecnologias

### Tecnologias

**Backend:**
- FastAPI 0.109+ (Python 3.11)
- PostgreSQL 16 (SQLAlchemy 2.0)
- Redis 7.2 (cache + sessions)
- Alembic (migrations)
- Pytest (testes)
- Docker Compose

**APIs Externas:**
- Google Books API (busca de livros)
- Hugging Face Inference API (Llama 3.1 8B Instruct)

**Frontend (em desenvolvimento):**
- React Native + Expo (mobile)
- React + Vite + Tailwind (web)
- TypeScript + Zustand

## 🏗️ Arquitetura

```
book2game/
├── backend/                 # FastAPI + Python 3.11
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Config, security, logging
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── crud/           # Database operations
│   ├── tests/
│   │   ├── unit/          # 60% coverage target
│   │   ├── integration/   # 30% coverage target
│   │   └── e2e/           # 10% coverage target
│   └── alembic/           # Database migrations
├── frontend/
│   └── packages/
│       ├── shared/        # API client, hooks, types
│       ├── mobile/        # React Native + Expo
│       └── web/           # React + Vite
└── docker-compose.yml
```

## 🚀 Setup Local

### Pré-requisitos

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (para frontend)
- pnpm (para monorepo frontend)

### Configuração

1. **Clone e configure variáveis de ambiente:**

```bash
git clone <repository-url>
cd book2game
```

**⚠️ IMPORTANTE**: O arquivo `.env` já foi criado para você, mas você precisa **configurar suas API keys**:

📖 **Siga o guia completo**: [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)

Ou configure manualmente:
- **Google Books API**: https://console.cloud.google.com/apis/credentials
- **Hugging Face API**: https://huggingface.co/settings/tokens
- **SECRET_KEY**: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

Edite o arquivo `.env` e substitua `SUA-CHAVE-AQUI` pelas suas keys reais.

2. **Inicie os serviços com Docker:**

```bash
docker-compose up -d
```

Serviços disponíveis:
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Redis Commander**: http://localhost:8081 (visualização web do cache)

3. **Execute migrations:**

```bash
docker-compose exec backend alembic upgrade head
```

## 🔍 Visualizar Cache Redis

Acesse **Redis Commander** em http://localhost:8081 para:
- Inspecionar keys de cache (livros, jogos, recomendações)
- Verificar TTLs e expirações
- Executar comandos Redis manualmente (GET, SET, EXPIRE, DEL)
- Monitorar hit rate do cache

Ou via CLI:
```bash
docker-compose exec redis redis-cli
> KEYS *
> GET book:harry_potter
> TTL book:harry_potter
```

## 🧪 Rodar Testes

```bash
# Todos os testes unitários (49 testes - 100% passing)
docker-compose exec backend pytest tests/unit/test_services/ -v --no-cov

# Com coverage report
docker-compose exec backend pytest tests/unit/ -v --cov=app --cov-report=html

# Teste específico
docker-compose exec backend pytest tests/unit/test_services/test_recommendation_service.py -v

# Ver relatório HTML de coverage
# Arquivo gerado em: backend/htmlcov/index.html
```

**Status Atual dos Testes:**
- ✅ Unit Tests: 49/49 passing (100%)
- ✅ AI Game Generator: 16 testes
- ✅ Recommendation Service: 12 testes
- ✅ Cache Service: 10 testes
- ✅ Google Books Service: 4 testes
- ✅ Hugging Face Service: 7 testes

**Próximos passos:**
- Integration tests (API endpoints)
- E2E tests (fluxo completo)

## 📖 Documentação Adicional

- [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md) - Como configurar Google Books e Hugging Face
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Guia completo de testes
- [INSOMNIA_GUIDE.md](INSOMNIA_GUIDE.md) - Coleção de requisições HTTP
- Swagger UI: http://localhost:8000/docs (quando rodando)

## 📝 Conventional Commits

Este projeto segue [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: adicionar endpoint de busca de livros
fix: corrigir validação de email no registro
test: adicionar testes para serviço de cache
docs: atualizar README com instruções Redis
refactor: extrair lógica de mapeamento para service
```

Tipos permitidos: `feat`, `fix`, `test`, `docs`, `refactor`, `style`, `chore`, `perf`

Pre-commit hooks validarão automaticamente.

## 🚢 Deploy

### ⚠️ Importante: Segurança

**Antes de fazer deploy, certifique-se de:**
1. ✅ `.env` está no `.gitignore` (JÁ CONFIGURADO)
2. ✅ Nunca commitar API keys, tokens ou secrets
3. ✅ Usar variáveis de ambiente no serviço de deploy
4. ✅ Gerar nova `SECRET_KEY` para produção
5. ✅ Configurar `ENVIRONMENT=production` no deploy

### Railway (Recomendado para MVP)

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login e deploy
railway login
railway up
```

Variáveis de ambiente serão lidas do `.env` ou configuradas no dashboard Railway.

### Render (Production - futuro)

1. Criar Web Service apontando para `backend/`
2. Adicionar PostgreSQL e Redis add-ons
3. Configurar variáveis de ambiente
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

## 🔧 Troubleshooting

### Backend não conecta ao PostgreSQL
```bash
# Verificar health do postgres
docker-compose ps
docker-compose logs postgres

# Recriar volume se necessário
docker-compose down -v
docker-compose up -d
```

### Redis cache não funciona
```bash
# Verificar conexão Redis
docker-compose exec backend python -c "import redis; r=redis.from_url('redis://redis:6379/0'); print(r.ping())"

# Deve retornar: True
```

### Coverage abaixo de 80%
```bash
# Ver arquivos com baixa coverage
pytest --cov=app --cov-report=term-missing

# Focar em adicionar testes para arquivos reportados
```

### Hugging Face API timeout
- Verifique `AI_REQUEST_TIMEOUT` no `.env` (padrão: 30s)
- Sistema usa retry exponential backoff (3 tentativas)
- Fallback manual ativará se todas tentativas falharem

## 📊 Métricas e Logging

Logs estruturados em JSON com loguru:
- `request_id` para rastreamento
- `duration` para performance
- `cache_hit_rate` para eficiência
- Rotação: 10MB
- Retenção: 7 dias

```bash
# Ver logs do backend
docker-compose logs -f backend

# Filtrar por level
docker-compose logs backend | grep ERROR
```

## 🤝 Contribuindo

1. Clone o repositório: `git clone <repo-url>`
2. Crie uma branch: `git checkout -b feat/nova-funcionalidade`
3. Configure o `.env` (copie do `.env.example` e adicione suas keys)
4. Suba os containers: `docker-compose up -d`
5. Rode os testes: `pytest tests/unit/ -v`
6. Faça commits seguindo [Conventional Commits](https://www.conventionalcommits.org/)
7. Push: `git push origin feat/nova-funcionalidade`
8. Abra Pull Request

**Tipos de commit:**
- `feat:` nova funcionalidade
- `fix:` correção de bug
- `test:` adicionar/atualizar testes
- `docs:` atualizar documentação
- `refactor:` refatoração de código
- `chore:` tarefas de manutenção

## 🔒 Segurança

### ✅ Validações Implementadas

1. **Secrets gerenciados via `.env`**
   - Arquivo `.env` está no `.gitignore`
   - Template `.env.example` sem valores reais
   - Validação de `SECRET_KEY` (mínimo 32 caracteres)

2. **Nenhuma credencial hardcoded**
   - Todas as keys via `pydantic-settings`
   - Configuração centralizada em `app/core/config.py`
   - Valores opcionais com fallbacks seguros

3. **Git protegido**
   - `.gitignore` completo (env, keys, certs, backups)
   - Histórico limpo (sem commits de secrets)
   - Pre-commit hooks configurados

4. **Rate Limiting ativo**
   - Auth: 5 requisições/minuto
   - Geral: 60 requisições/minuto

5. **JWT seguro**
   - Access token: 15 minutos
   - Refresh token: 7 dias
   - Algoritmo HS256

### 🚨 Nunca commite:
- ❌ Arquivos `.env` com keys reais
- ❌ Tokens de API (Hugging Face, Google Books)
- ❌ Credenciais de banco de dados
- ❌ Certificados ou chaves privadas (.pem, .key)
- ❌ Backups de banco de dados (.sql, .db)

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🔗 Links Úteis

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Google Books API](https://developers.google.com/books)
- [Hugging Face Models](https://huggingface.co/models)
- [Llama 3.1 8B Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)
- [Redis Commands](https://redis.io/commands/)
