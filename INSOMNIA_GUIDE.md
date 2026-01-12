# 🧪 Guia de Testes Manuais - Book2Game API

## 📥 Importar Coleção no Insomnia

### Método 1: Importar Arquivo JSON (Recomendado)

1. Abra o **Insomnia**
2. Clique em **Create** → **Import From File**
3. Selecione o arquivo `insomnia_collection.json` (raiz do projeto)
4. ✅ Pronto! Todos os 16 endpoints estarão organizados em pastas

### Método 2: Importar do Swagger (Alternativo)

1. Certifique-se que o backend está rodando (`docker-compose up -d`)
2. No Insomnia: **Create** → **Import From URL**
3. Cole: `http://localhost:8000/openapi.json`

---

## 🚀 Fluxo de Teste Completo

### **Passo 1: Configurar Variáveis de Ambiente**

No Insomnia, configure as variáveis no ambiente **Development**:

```json
{
  "base_url": "http://localhost:8000/api/v1",
  "access_token": "",
  "test_email": "seu_email@example.com",
  "test_password": "sua_senha123"
}
```

### **Passo 2: Autenticação (Obrigatório)**

#### 2.1 Registrar Usuário
```
📁 Authentication → Register User
```
- ✅ Status esperado: `201 Created`
- 📝 Resposta: Dados do usuário criado

#### 2.2 Fazer Login
```
📁 Authentication → Login
```
- ✅ Status esperado: `200 OK`
- 📝 Resposta contém:
  - `access_token` ← **COPIE ESTE TOKEN**
  - `refresh_token`
  - `token_type`: "bearer"

#### 2.3 Configurar Token
1. Copie o `access_token` da resposta do login
2. Vá em **Manage Environments** (⚙️ no canto superior direito)
3. Cole o token na variável `access_token`
4. **Salve** ✅

---

### **Passo 3: Testar Endpoints de Livros**

#### 3.1 Buscar Livros
```
📁 Books → Search Books
Query: Harry Potter
```
- ✅ Status: `200 OK`
- 📊 Retorna lista de livros do Google Books
- 🔍 Cache de 24 horas

#### 3.2 Detalhes de um Livro
```
📁 Books → Get Book Details
Book ID: zyTCAlFPjgYC (Harry Potter)
```
- ✅ Status: `200 OK`
- 📖 Detalhes completos do livro

---

### **Passo 4: Testar Endpoints de Jogos**

#### 4.1 Buscar Jogos por Nome
```
📁 Games → Search Games
Query: witcher
```
- ✅ Status: `200 OK`
- 🎮 Lista de jogos recomendados (gerados pela IA)

#### 4.2 Buscar Jogos por Tags
```
📁 Games → Search by Tags
Tags: fantasy,magic,adventure
```
- ✅ Status: `200 OK`
- 🏷️ Jogos filtrados por tags

---

### **Passo 5: Testar Sistema de Recomendação (Principal) ⭐**

#### 5.1 Gerar Recomendação com IA
```
📁 Recommendations → Generate Recommendation ⭐
Body: { "book_id": "zyTCAlFPjgYC" }
```
- ⏱️ **Aguarde 5-30 segundos** (processamento de IA)
- ✅ Status: `201 Created`
- 🤖 Resposta contém jogos recomendados + scores

**⚠️ Rate Limit:** 10 requests por hora

---

### **Passo 6: Testar Perfil de Usuário**

#### 6.1 Ver Meu Perfil
```
📁 Users → Get My Profile
```
- ✅ Status: `200 OK`

#### 6.2 Atualizar Perfil
```
📁 Users → Update Profile
Body: { "full_name": "Novo Nome" }
```
- ✅ Status: `200 OK`

---

## 📊 Checklist de Testes Completos

### Authentication (3 endpoints)
- [x] POST /auth/register
- [x] POST /auth/login
- [x] POST /auth/refresh-token

### Books (3 endpoints)
- [x] GET /books/search
- [x] GET /books/{book_id}
- [x] POST /books/

### Games (4 endpoints)
- [ ] GET /games/search
- [ ] GET /games/{game_id}
- [ ] GET /games/tags/{tags}
- [ ] POST /games/

### Recommendations (3 endpoints) ⭐
- [ ] POST /recommendations/ (principal)
- [ ] GET /recommendations/
- [ ] GET /recommendations/{id}

### Users (3 endpoints)
- [ ] GET /users/me
- [ ] PUT /users/me
- [ ] GET /users/me/recommendations

### Total: 16 endpoints

---

## 🎯 Fluxo de Teste Rápido (5 minutos)

1. ✅ Register → Login → Copiar token
2. ✅ Search Books ("Harry Potter")
3. ✅ Search Games ("witcher")
4. ✅ Generate Recommendation (usar book_id de Harry Potter)
5. ✅ Get My Profile

**Pronto! API validada.** 🚀

---

## 🔗 Links Úteis

- **Swagger UI:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## 💡 Dicas

1. **Use o Swagger primeiro** para entender os schemas
2. **Salve tokens em variáveis** para não copiar/colar toda hora
3. **Teste cenários de erro** (não só happy path)
4. **Monitore logs** se algo não funcionar: `docker-compose logs -f backend`
