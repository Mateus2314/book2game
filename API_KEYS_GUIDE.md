# 🔐 Guia de Configuração de API Keys

## Como obter suas API Keys

### 1. Google Books API (Gratuita)
1. Acesse: https://console.cloud.google.com/
2. Crie um projeto novo ou selecione existente
3. Vá em **APIs & Services** > **Library**
4. Procure "Books API" e clique em **Enable**
5. Vá em **Credentials** > **Create Credentials** > **API key**
6. Copie a chave e cole em `.env`: `GOOGLE_BOOKS_API_KEY=sua-chave`

**Limite gratuito**: 1.000 requisições/dia

---

### 2. Hugging Face API (Gratuita)
1. Acesse: https://huggingface.co/join
2. Crie uma conta gratuita
3. Vá em **Settings** > **Access Tokens**
4. Clique em **New token** > escolha tipo **Read**
5. Copie o token e cole em `.env`: `HUGGINGFACE_API_KEY=hf_xxx`

**Modelos usados:**
- **Classificação**: ProsusAI/finbert
- **Geração de Jogos**: meta-llama/Llama-3.1-8B-Instruct

**Limite gratuito**: Rate limiting generoso para projetos pessoais

---

### 3. Gerar SECRET_KEY Segura
Execute no terminal:

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# PowerShell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copie a saída e cole em `.env`: `SECRET_KEY=sua-chave-gerada`

---

## Verificar Configuração

Após configurar todas as keys, verifique:

```bash
# Ver arquivo .env (sem mostrar secrets)
cat .env | grep -E "API_KEY|SECRET_KEY" | sed 's/=.*/=***/'

# Testar conexão Redis
docker-compose up -d redis
docker-compose exec backend python -c "import redis; r=redis.from_url('redis://redis:6379/0'); print('Redis OK!' if r.ping() else 'Erro')"
```

---

## Segurança

✅ **Boas práticas implementadas**:
- `.env` está no `.gitignore` (NÃO vai para o Git)
- `.env.example` é o template público (sem secrets)
- `SECRET_KEY` validada com mínimo 32 caracteres
- Email validation com regex
- Rate limiting em endpoints sensíveis

❌ **NUNCA faça**:
- Commit do arquivo `.env` real
- Compartilhe suas API keys em público
- Use keys de produção em desenvolvimento

---

## Teste Rápido

```bash
# 1. Suba os containers
docker-compose up -d

# 2. Acesse a API
curl http://localhost:8000/health

# 3. Veja logs
docker-compose logs -f backend

# 4. Redis Commander (visualizar cache)
http://localhost:8081
```

---

## Troubleshooting

**Erro: "SECRET_KEY must be at least 32 characters"**
→ Gere uma nova chave com o comando Python acima

**Erro: "Redis connection failed"**
→ Verifique se o container Redis está rodando: `docker-compose ps`

**Erro: "Invalid API key" em external APIs**
→ Verifique se copiou as keys corretamente (sem espaços extras)

---

## Links Úteis

- [Google Cloud Console](https://console.cloud.google.com/)
- [Hugging Face Tokens](https://huggingface.co/settings/tokens)
- [Llama 3.1 Model](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)
- [Docker Compose](https://docs.docker.com/compose/)
