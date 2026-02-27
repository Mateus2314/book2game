# Script para executar todos os testes e gerar relatório
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Executando Testes - Book2Game Backend" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Testes Unitários
Write-Host "[1/4] Testes Unitarios..." -ForegroundColor Yellow
$unitResult = pytest tests/unit/ --no-cov -q 2>&1 | Out-String
if ($unitResult -match "(\d+) passed") {
    Write-Host "OK Unitarios: $($Matches[1]) passaram" -ForegroundColor Green
}

# Testes de Autenticacao
Write-Host "[2/4] Testes de Autenticacao..." -ForegroundColor Yellow  
$authResult = pytest tests/integration/test_auth.py --no-cov -q 2>&1 | Out-String
if ($authResult -match "(\d+) passed") {
    $authPassed = $Matches[1]
    if ($authResult -match "(\d+) failed") {
        Write-Host "AVISO Autenticacao: $authPassed passaram, $($Matches[1]) falharam" -ForegroundColor Yellow
    } else {
        Write-Host "OK Autenticacao: $authPassed passaram" -ForegroundColor Green
    }
}

# Testes de Usuarios
Write-Host "[3/4] Testes de Usuarios..." -ForegroundColor Yellow
$usersResult = pytest tests/integration/test_users.py --no-cov -q 2>&1 | Out-String
if ($usersResult -match "(\d+) passed") {
    Write-Host "OK Usuarios: $($Matches[1]) passaram" -ForegroundColor Green
}

# Testes de Games
Write-Host "[4/4] Testes de Games..." -ForegroundColor Yellow
$gamesResult = pytest tests/integration/test_games.py --no-cov -q 2>&1 | Out-String
if ($gamesResult -match "(\d+) passed") {
    Write-Host "OK Games: $($Matches[1]) passaram" -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan  
Write-Host "Relatório Final" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Total
Write-Host ""
Write-Host "Executando contagem total..." -ForegroundColor Yellow
$totalResult = pytest --no-cov --co -q 2>&1 | Out-String
if ($totalResult -match "(\d+) tests? collected") {
    Write-Host "TOTAL: $($Matches[1]) testes implementados" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Testes concluidos!" -ForegroundColor Green
