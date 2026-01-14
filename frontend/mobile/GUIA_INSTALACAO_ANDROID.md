# 🚀 Guia Completo de Instalação - Android Studio + React Native

## 📋 Pré-requisitos

### 1. Node.js (versão 18 ou superior)

1. Baixe em: https://nodejs.org/
2. Instale a versão LTS (Long Term Support)
3. Verifique a instalação:
```powershell
node --version
npm --version
```

---

## ☕ 2. Instalar Java JDK 17

### Download e Instalação

1. **Baixe o JDK 17** (Temurin):
   - URL: https://adoptium.net/temurin/releases/
   - Escolha: **Version 17 (LTS)**, **Windows x64**, **JDK**, **MSI**

2. **Execute o instalador**:
   - Deixe as opções padrão
   - Caminho padrão: `C:\Program Files\Eclipse Adoptium\jdk-17.x.x-hotspot`

3. **Verificar instalação**:
```powershell
java -version
# Deve mostrar: openjdk version "17.x.x"
```

### Configurar Variáveis de Ambiente

1. **Abra Variáveis de Ambiente**:
   - Pressione `Win + X` → Selecione "Sistema"
   - Clique em "Configurações avançadas do sistema"
   - Clique em "Variáveis de Ambiente..."

2. **Criar JAVA_HOME** (Variáveis do Sistema):
   - Clique em "Novo..." na seção "Variáveis do sistema"
   - Nome da variável: `JAVA_HOME`
   - Valor: `C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot` (ajuste a versão)
   - Clique em "OK"

3. **Adicionar ao Path**:
   - Selecione a variável "Path" em "Variáveis do sistema"
   - Clique em "Editar..."
   - Clique em "Novo"
   - Adicione: `%JAVA_HOME%\bin`
   - Clique em "OK"

4. **Verificar**:
```powershell
# Feche e abra novo terminal PowerShell
echo $env:JAVA_HOME
javac -version
```

---

## 📱 3. Instalar Android Studio

### Download

1. Baixe em: https://developer.android.com/studio
2. Execute o instalador: `android-studio-xxxx.exe`
3. **Durante a instalação, marque**:
   - ✅ Android Studio
   - ✅ Android SDK
   - ✅ Android SDK Platform
   - ✅ Android Virtual Device

### Configuração Inicial

1. **Abra o Android Studio**
2. **Setup Wizard**:
   - Clique em "Next"
   - Install Type: **Standard**
   - Selecione o tema (pode deixar Darcula ou Light)
   - Clique em "Next" → "Finish"
   - Aguarde o download de componentes (pode demorar 10-30 minutos)

### Instalar SDKs e Ferramentas

1. **Abra SDK Manager**:
   - No Android Studio, vá em: `File > Settings` (ou `Ctrl + Alt + S`)
   - Navegue: `Appearance & Behavior > System Settings > Android SDK`

2. **Aba "SDK Platforms"**:
   - ✅ Marque: **Android 13.0 (Tiramisu)** - API Level 33
   - ✅ Marque a opção "Show Package Details" (canto inferior direito)
   - Dentro de Android 13.0, marque:
     - ✅ Android SDK Platform 33
     - ✅ Intel x86 Atom_64 System Image (para emulador)
     - ✅ Google APIs Intel x86 Atom System Image

3. **Aba "SDK Tools"**:
   - ✅ Android SDK Build-Tools 33.0.0
   - ✅ Android Emulator
   - ✅ Android SDK Platform-Tools
   - ✅ Android SDK Tools (Obsolete) - se disponível
   - ✅ Google Play services
   - ✅ Intel x86 Emulator Accelerator (HAXM installer)

4. **Clique em "Apply"** → "OK"
   - Aguarde o download e instalação

### Configurar Variáveis de Ambiente do Android

1. **Caminho padrão do SDK**:
   - `C:\Users\SEU_USUARIO\AppData\Local\Android\Sdk`
   - Você pode ver o caminho no SDK Manager (Android SDK Location)

2. **Criar ANDROID_HOME**:
   - Abra "Variáveis de Ambiente" (Win + X → Sistema → Avançado)
   - Em "Variáveis do sistema", clique em "Novo..."
   - Nome: `ANDROID_HOME`
   - Valor: `C:\Users\SEU_USUARIO\AppData\Local\Android\Sdk` (substitua SEU_USUARIO)

3. **Adicionar ao Path**:
   - Selecione "Path" em "Variáveis do sistema"
   - Clique em "Editar..."
   - Adicione as seguintes linhas (clique em "Novo" para cada):
   ```
   %ANDROID_HOME%\platform-tools
   %ANDROID_HOME%\emulator
   %ANDROID_HOME%\tools
   %ANDROID_HOME%\tools\bin
   ```

4. **Verificar**:
```powershell
# Feche e abra novo PowerShell
echo $env:ANDROID_HOME
adb version
```

---

## 🖥️ 4. Criar Emulador Android

1. **No Android Studio, clique em**: `Tools > Device Manager` (ou ícone de celular na barra)

2. **Criar Virtual Device**:
   - Clique em "Create Device"
   - Escolha: **Pixel 5** (ou qualquer dispositivo moderno)
   - Clique em "Next"

3. **Selecione System Image**:
   - Aba "Recommended"
   - Escolha: **Tiramisu (API Level 33)** - Google APIs
   - Se não estiver instalada, clique em "Download" ao lado
   - Clique em "Next"

4. **Configurar AVD**:
   - AVD Name: `Pixel_5_API_33` (ou deixe o padrão)
   - Startup orientation: Portrait
   - Clique em "Show Advanced Settings"
   - **RAM**: 2048 MB (mínimo) ou 4096 MB (recomendado)
   - **VM heap**: 512 MB
   - **Internal Storage**: 2048 MB
   - **SD Card**: 512 MB
   - Clique em "Finish"

---

## 🚀 5. Configurar e Rodar o Projeto Book2Game

### Navegar até o Projeto

```powershell
cd C:\Users\mfuentec\Documents\projeto-python\book2game\frontend\mobile
```

### Instalar Dependências

```powershell
npm install
```

### Configurar Variáveis de Ambiente

Edite o arquivo `.env` na pasta `mobile/`:

```env
# Para emulador Android (sempre use 10.0.2.2)
API_URL=http://10.0.2.2:8000/api/v1

# Para dispositivo físico (use o IP da sua máquina)
# API_URL=http://192.168.0.10:8000/api/v1
```

**Importante**: 
- `10.0.2.2` é o IP especial do emulador Android para acessar localhost da máquina host
- Para dispositivo físico via USB, use o IP real da sua máquina na rede

### Iniciar o Backend (em outro terminal)

```powershell
# Terminal 1 - Backend
cd C:\Users\mfuentec\Documents\projeto-python\book2game
docker-compose up
```

### Iniciar o Metro Bundler

```powershell
# Terminal 2 - Metro Bundler
cd C:\Users\mfuentec\Documents\projeto-python\book2game\frontend\mobile
npm start
```

### Iniciar o Emulador

**Opção 1: Pelo Android Studio**
- Abra o Device Manager
- Clique no ▶️ (Play) ao lado do seu emulador

**Opção 2: Pelo Terminal**
```powershell
# Terminal 3 - Emulador
emulator -avd Pixel_5_API_33
```

### Rodar o App no Emulador

```powershell
# Terminal 4 - Build e Deploy
cd C:\Users\mfuentec\Documents\projeto-python\book2game\frontend\mobile
npm run android
```

Ou se já tiver o Metro Bundler rodando, apenas:
```powershell
npx react-native run-android
```

---

## 🔧 Troubleshooting Comum

### Erro: "SDK location not found"

```powershell
# Criar arquivo local.properties em mobile/android/
cd C:\Users\mfuentec\Documents\projeto-python\book2game\frontend\mobile\android
echo sdk.dir=C:\\Users\\SEU_USUARIO\\AppData\\Local\\Android\\Sdk > local.properties
```

### Erro: "JAVA_HOME is not set"

```powershell
# Verificar JAVA_HOME
echo $env:JAVA_HOME

# Se estiver vazio, configure novamente as variáveis de ambiente
```

### Erro: "Unable to load script"

```powershell
# Limpar cache e rebuild
cd C:\Users\mfuentec\Documents\projeto-python\book2game\frontend\mobile
npx react-native start --reset-cache
```

### Emulador muito lento

1. **Habilitar Hyper-V** (Windows 10/11 Pro):
   - Painel de Controle → Programas → Ativar/Desativar Recursos do Windows
   - Marque: ✅ Hyper-V
   - Reinicie o PC

2. **Ou use dispositivo físico via USB**:
   - Habilite "Modo Desenvolvedor" no Android
   - Habilite "Depuração USB"
   - Conecte via USB
   - Execute: `adb devices` (deve aparecer seu dispositivo)

### Porta 8081 em uso

```powershell
# Matar processo na porta 8081
netstat -ano | findstr :8081
taskkill /PID <NUMERO_DO_PID> /F

# Ou iniciar Metro em outra porta
npx react-native start --port 8082
```

---

## ✅ Checklist de Verificação

Antes de rodar o projeto, verifique:

- [ ] `node --version` funciona (v18+)
- [ ] `java -version` funciona (17.x)
- [ ] `echo $env:JAVA_HOME` mostra o caminho do JDK
- [ ] `echo $env:ANDROID_HOME` mostra o caminho do SDK
- [ ] `adb version` funciona
- [ ] Emulador criado no Device Manager
- [ ] Backend rodando em http://localhost:8000
- [ ] `.env` configurado com `API_URL=http://10.0.2.2:8000/api/v1`
- [ ] `npm install` executado sem erros

---

## 🎯 Comandos Úteis

```powershell
# Listar dispositivos conectados
adb devices

# Limpar build do Android
cd android
.\gradlew clean
cd ..

# Rebuild completo
npx react-native run-android --reset-cache

# Ver logs do Android
adb logcat | Select-String "ReactNativeJS"

# Abrir menu de desenvolvedor no emulador
# Pressione Ctrl + M no emulador

# Recarregar app
# Pressione R + R no emulador (duplo R)
```

---

## 📱 Próximos Passos

Após configurar tudo:

1. ✅ Teste o login no app
2. ✅ Busque um livro
3. ✅ Gere recomendações de jogos
4. ✅ Verifique a biblioteca
5. ✅ Teste o perfil

Se tudo funcionar, você terá um ambiente React Native completo! 🎉

---

## 🆘 Suporte

Se encontrar problemas:
1. Verifique o checklist acima
2. Consulte o Troubleshooting
3. Verifique os logs: `adb logcat`
4. Reinicie: emulador, Metro Bundler, Android Studio

**Boa sorte!** 🚀
