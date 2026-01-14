# Book2Game Mobile App

Aplicativo mobile React Native para descobrir jogos baseados em livros usando IA (Llama 3.1).

## 🚀 Tecnologias

- **React Native** 0.73
- **TypeScript**
- **React Native Paper** (Material Design 3)
- **React Navigation** (Stack + Bottom Tabs)
- **React Query** (TanStack Query)
- **Axios** (HTTP client)
- **React Hook Form + Zod** (Validação de formulários)
- **Zustand** (Gerenciamento de estado)
- **AsyncStorage** (Persistência local)

## 📋 Pré-requisitos

### Windows

1. **Node.js** 18+ ([Download](https://nodejs.org/))
2. **JDK 17** ([Download](https://adoptium.net/))
3. **Android Studio** ([Download](https://developer.android.com/studio))
   - Android SDK Platform 33
   - Android SDK Build-Tools
   - Android Emulator

### Variáveis de Ambiente

Configure as variáveis de ambiente do Android:

```powershell
# Adicione ao Path do sistema:
C:\Users\<SEU_USUARIO>\AppData\Local\Android\Sdk\platform-tools
C:\Users\<SEU_USUARIO>\AppData\Local\Android\Sdk\tools
C:\Users\<SEU_USUARIO>\AppData\Local\Android\Sdk\emulator

# Crie a variável ANDROID_HOME:
C:\Users\<SEU_USUARIO>\AppData\Local\Android\Sdk

# Crie a variável JAVA_HOME:
C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot
```

## 📦 Instalação

1. **Instalar dependências**:

```powershell
cd c:\Users\mfuentec\Documents\projeto-python\book2game\frontend\mobile
npm install
```

2. **Configurar variáveis de ambiente**:

Edite o arquivo `.env` e configure a URL do backend:

```env
API_URL=http://10.0.2.2:8000/api/v1  # Para emulador Android
# OU
API_URL=http://SEU_IP:8000/api/v1     # Para dispositivo físico
```

> **Nota**: `10.0.2.2` é o IP que o emulador Android usa para acessar o localhost da máquina host.

3. **Iniciar Metro Bundler**:

```powershell
npm start
```

4. **Executar no Android** (em outro terminal):

```powershell
npm run android
```

## 🏗️ Estrutura do Projeto

```
src/
├── components/       # Componentes reutilizáveis
│   ├── common/       # RatingStars, StatusChip, EmptyState
│   ├── books/        # BookCard
│   └── games/        # GameCard, GameDetailsModal
├── screens/          # Telas da aplicação
│   ├── auth/         # Login, Register
│   ├── home/         # HomeScreen (busca)
│   ├── books/        # BookDetailsScreen
│   ├── recommendations/  # RecommendationResultsScreen
│   ├── library/      # LibraryScreen
│   └── profile/      # ProfileScreen, EditProfileScreen
├── services/         # Lógica de negócio
│   ├── api/          # Axios config, endpoints
│   └── auth/         # authStorage (AsyncStorage)
├── navigation/       # Configuração de navegação
├── stores/           # Zustand stores (authStore)
├── hooks/            # Hooks customizados (useDebounce, useErrorHandler)
├── schemas/          # Schemas Zod (validação)
├── types/            # TypeScript types
├── theme/            # Tema Material Design 3
└── utils/            # Utilitários (gameIcons)
```

## 🎨 Features Implementadas

### ✅ Autenticação
- Login com email e senha
- Registro de novos usuários
- Refresh automático de tokens JWT
- Persistência de sessão

### ✅ Busca de Livros
- Busca na Google Books API
- Debounce de 500ms
- Infinite scroll (paginação automática)
- Pull-to-refresh

### ✅ Recomendações de Jogos
- Geração via IA Llama 3.1 (5-10s)
- Loading dialog durante processamento
- Score de similaridade visual
- Modal de detalhes completos do jogo

### ✅ Bibliotecas Pessoais
- Biblioteca de livros e jogos
- Filtros por status e favoritos
- Adicionar/remover itens

### ✅ Perfil do Usuário
- Visualização de dados
- Edição de nome, email e senha
- Histórico de recomendações
- Logout

## 🎯 Próximos Passos

- [ ] Implementar EditMetadataModal (rating, notas, status, horas jogadas)
- [ ] Adicionar filtros avançados na biblioteca
- [ ] Implementar busca de jogos por tags
- [ ] Adicionar dark mode toggle
- [ ] Melhorar tratamento de erros offline
- [ ] Adicionar testes unitários
- [ ] Configurar CI/CD

## 🐛 Debug

### Metro Bundler não inicia
```powershell
npm start -- --reset-cache
```

### Erro de Build Android
```powershell
cd android
.\gradlew clean
cd ..
npm run android
```

### Erro de permissão Android
```powershell
# Execute como Administrador
npm run android
```

## 📱 Testando

### Emulador Android
1. Abra Android Studio
2. AVD Manager → Create Virtual Device
3. Escolha Pixel 5 + API 33
4. Execute `npm run android`

### Dispositivo Físico
1. Ative "Depuração USB" nas Opções do Desenvolvedor
2. Conecte via USB
3. Execute `npm run android`
4. Configure `.env` com IP da máquina (não use localhost)

## 🔗 Backend

Este app requer o backend Book2Game rodando em:
- Local: `http://localhost:8000`
- Emulador: `http://10.0.2.2:8000`

Veja o README do backend para instruções de setup.

## 📄 Licença

MIT
