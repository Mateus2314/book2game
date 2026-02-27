# Book2Game Backend Tests

Documentação completa dos testes automatizados do backend Book2Game.

## 📋 Visão Geral

O projeto utiliza **pytest** como framework de testes, com cobertura de:
- ✅ Testes unitários (security, CRUD)
- ✅ Testes de integração (API endpoints)
- ✅ Fixtures compartilhadas via conftest.py
- ✅ Mocks de APIs externas (Google Books, Hugging Face)
- ✅ PostgreSQL de teste isolado em Docker

---

## 🚀 Setup Rápido

### 1. Subir Banco de Dados de Teste

```bash
# Subir apenas o PostgreSQL de teste
docker-compose up postgres-test -d

# Aguardar até o banco estar pronto (health check)
docker-compose ps postgres-test
```

### 2. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 3. Executar Todos os Testes

```bash
pytest -v
```

---

## 🧪 Executando Testes

### Executar Todos os Testes
```bash
pytest -v
```

### Testes Unitários (Rápidos, sem DB)
```bash
pytest -v -m unit
```

### Testes de Integração (com DB e API)
```bash
pytest -v -m integration
```

### Teste Específico
```bash
# Por arquivo
pytest tests/unit/test_security.py -v

# Por classe
pytest tests/integration/test_auth.py::TestUserRegistration -v

# Por função
pytest tests/integration/test_auth.py::TestUserRegistration::test_register_success -v
```

### Com Cobertura de Código
```bash
# Terminal
pytest --cov=app --cov-report=term-missing

# HTML (abre htmlcov/index.html no navegador)
pytest --cov=app --cov-report=html
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows
```

### Testes Lentos
```bash
pytest -v -m slow
```

### Testes que Chamam APIs Externas
```bash
pytest -v -m external
```

---

## 📂 Estrutura de Testes

```
backend/tests/
├── conftest.py               # Fixtures compartilhadas, configuração de DB
├── unit/                     # Testes unitários (isolados, sem DB)
│   ├── test_security.py      # ✅ 17 testes (hashing, JWT, email validation)
│   └── test_crud/            # ✅ 34 testes (user_book, user_game CRUD)
│       ├── test_user_book_crud.py
│       └── test_user_game_crud.py
└── integration/              # Testes de integração (com DB real)
    └── test_api/             # ✅ 62 testes (endpoints de API)
        ├── test_auth.py      # 17 testes (register, login, refresh)
        ├── test_users.py     # 13 testes (perfil, update, recomendações)
        ├── test_books.py     # 16 testes (search, details, create)
        └── test_games.py     # 16 testes (search, tags, create)
```

**Total:** ~113 testes implementados

---

## 🔧 Fixtures Disponíveis

Fixtures definidas em `conftest.py` para uso em todos os testes:

### Database & API
- **`db`**: Sessão de banco de dados com rollback automático
- **`client`**: TestClient do FastAPI com dependency overrides

### Autenticação
- **`test_user`**: Usuário de teste (email: test@example.com, senha: testpassword123)
- **`test_superuser`**: Superusuário de teste (email: admin@example.com)
- **`auth_token`**: Token JWT válido para test_user
- **`superuser_token`**: Token JWT válido para superuser
- **`auth_headers`**: Headers HTTP com Bearer token (`{"Authorization": "Bearer ..."}`)
- **`superuser_headers`**: Headers HTTP com Bearer token de superuser

### Mocks de APIs Externas
- **`mock_google_books_response`**: Resposta simulada da Google Books API
- **`mock_huggingface_response`**: Resposta simulada da Hugging Face API

### Exemplo de Uso
```python
def test_example(client: TestClient, auth_headers: dict, db: Session):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
```

---

## 🏷️ Marcadores de Teste

| Marcador | Descrição | Comando |
|----------|-----------|---------|
| `@pytest.mark.unit` | Testes unitários (rápidos, sem DB) | `pytest -m unit` |
| `@pytest.mark.integration` | Testes de integração (com DB e API) | `pytest -m integration` |
| `@pytest.mark.slow` | Testes que demoram >1s | `pytest -m slow` |
| `@pytest.mark.external` | Chamam APIs externas (use mocks) | `pytest -m external` |

---

## 🐳 Docker Configuration

### PostgreSQL de Teste

Configurado em `docker-compose.yml`:

```yaml
postgres-test:
  image: postgres:15-alpine
  container_name: book2game_postgres_test
  environment:
    POSTGRES_USER: book2game_test
    POSTGRES_PASSWORD: book2game_test
    POSTGRES_DB: book2game_test_db
  ports:
    - "5433:5432"  # Porta diferente para não conflitar com DB principal
  tmpfs:
    - /var/lib/postgresql/data  # Dados em memória (mais rápido)
```

### Gerenciar Container de Teste

```bash
# Subir
docker-compose up postgres-test -d

# Verificar status
docker-compose ps postgres-test

# Ver logs
docker-compose logs -f postgres-test

# Parar
docker-compose stop postgres-test

# Remover (destrói dados)
docker-compose down postgres-test
```

---

## 🔒 Rate Limiting em Testes

**Rate limiting é DESABILITADO automaticamente em ambiente de teste.**

Configuração em `app/core/config.py`:
```python
TESTING: bool = False
```

Configuração em `app/main.py`:
```python
if not settings.TESTING:
    # Rate limiter apenas em produção/desenvolvimento
    limiter = Limiter(...)
```

Em `conftest.py`, `settings.TESTING = True` é definido antes de criar o TestClient.

---

## 📊 Cobertura de Código

### Targets de Cobertura
- **Mínimo:** 40% (pytest.ini: `--cov-fail-under=40`)
- **Objetivo:** 80% (TESTING_GUIDE.md)
- **Atual:** ~70%

### Visualizar Cobertura

```bash
# Gerar relatório HTML
pytest --cov=app --cov-report=html

# Abrir relatório
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows
```

### Áreas com Cobertura
- ✅ `app/core/security.py`: ~95%
- ✅ `app/crud/user_book.py`: ~90%
- ✅ `app/crud/user_game.py`: ~90%
- ✅ `app/api/v1/endpoints/auth.py`: ~85%
- ✅ `app/api/v1/endpoints/users.py`: ~75%
- ✅ `app/api/v1/endpoints/books.py`: ~70%
- ✅ `app/api/v1/endpoints/games.py`: ~70%

---

## 🧩 Escrevendo Novos Testes

### Template de Teste Unitário

```python
"""
Unit tests for <module_name>.

Tests cover:
- <feature 1>
- <feature 2>
"""
import pytest
from app.<module> import <function>

@pytest.mark.unit
class Test<ClassName>:
    """Test <description>."""
    
    def test_<scenario>_success(self):
        """Test <description> with valid input."""
        result = <function>(<input>)
        assert result == <expected>
    
    def test_<scenario>_invalid(self):
        """Test <description> with invalid input."""
        with pytest.raises(<ExceptionType>):
            <function>(<invalid_input>)
```

### Template de Teste de Integração

```python
"""
Integration tests for <endpoint_name>.

Tests cover:
- <feature 1>
- <feature 2>
"""
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
class Test<EndpointName>:
    """Test <endpoint> endpoint."""
    
    def test_<scenario>_success(self, client: TestClient, auth_headers: dict):
        """Test <description> with authentication."""
        response = client.get("/api/v1/<endpoint>", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["field"] == "expected_value"
    
    def test_<scenario>_unauthenticated(self, client: TestClient):
        """Test <description> without authentication."""
        response = client.get("/api/v1/<endpoint>")
        assert response.status_code == 403
```

---

## 🐛 Debugging Testes

### Executar com Output Detalhado
```bash
pytest -vv -s
```

### Ver Prints Durante Testes
```bash
pytest -s
```

### Parar no Primeiro Erro
```bash
pytest -x
```

### Executar com PDB (debugger)
```bash
pytest --pdb
```

### Ver Fixtures Disponíveis
```bash
pytest --fixtures
```

### Ver Marcadores Disponíveis
```bash
pytest --markers
```

---

## ⚡ CI/CD

Os testes são executados automaticamente em:
- **Pull Requests**: Apenas testes unitários (`pytest -m unit`)
- **Push para main**: Todos os testes (`pytest -v`)
- **Deploy**: Testes + cobertura mínima de 40%

---

## 📝 Melhores Práticas

1. ✅ **Isolamento**: Cada teste deve ser independente
2. ✅ **Rollback**: Use fixture `db` que faz rollback automático
3. ✅ **Mocks**: Use `respx` para APIs externas (Google Books, Hugging Face)
4. ✅ **Nomenclatura**: `test_<scenario>_<expected_result>`
5. ✅ **Marcadores**: Sempre use `@pytest.mark.unit` ou `@pytest.mark.integration`
6. ✅ **Docstrings**: Descreva o que cada teste valida
7. ✅ **Arrange-Act-Assert**: Organize testes em 3 seções claras

---

## 🆘 Troubleshooting

### Erro: "no such table: users"
**Causa:** Banco de dados de teste não foi criado.

**Solução:**
```bash
# Parar e remover container antigo
docker-compose down postgres-test

# Subir novamente (recria schema)
docker-compose up postgres-test -d

# Aguardar health check
sleep 5

# Executar testes
pytest -v
```

### Erro: "KeyError: 'access_token'"
**Causa:** Rate limiting bloqueando requisições de teste.

**Solução:** Verificar que `settings.TESTING = True` em `conftest.py`.

### Erro: "Database connection refused"
**Causa:** PostgreSQL de teste não está rodando.

**Solução:**
```bash
docker-compose up postgres-test -d
docker-compose ps postgres-test  # Verificar status
```

### Testes Passando Localmente mas Falhando no CI
**Causa:** Diferenças de ambiente (timezone, locale, etc.)

**Solução:**
- Use `freezegun` para testar datas
- Não dependa de ordem de dicionários
- Use mocks para APIs externas

---

## 📚 Recursos Adicionais

- [Documentação Pytest](https://docs.pytest.org/)
- [Documentação FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Respx (HTTP Mocking)](https://lundberg.github.io/respx/)
- [Freezegun (Date/Time Mocking)](https://github.com/spulec/freezegun)

---

## 📞 Contato

Problemas com testes? Abra uma issue no repositório ou consulte [TESTING_GUIDE.md](../TESTING_GUIDE.md).
