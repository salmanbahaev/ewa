# PowerShell скрипт для загрузки проекта на VPS (Windows)

# Настройки (измени под себя)
$VPS_USER = "root"
$VPS_IP = "193.168.46.189"
$VPS_PATH = "/root/ewa"
$PROJECT_PATH = "D:\AI_PROJECTS\ewa"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📤 Загрузка EWA Bot на VPS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "VPS: $VPS_USER@$VPS_IP"
Write-Host "Путь: $VPS_PATH"
Write-Host ""

# Подтверждение
$confirm = Read-Host "Продолжить загрузку? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Отменено" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "🗑️ Очистка старой папки на VPS..." -ForegroundColor Yellow

# Очистка старой папки
ssh "$VPS_USER@$VPS_IP" "rm -rf $VPS_PATH && mkdir -p $VPS_PATH"

Write-Host "📦 Создание архива..." -ForegroundColor Yellow

# Временная папка для архива
$tempArchive = "$env:TEMP\ewa_deploy.tar.gz"

# Создание tar.gz архива (исключая ненужные файлы)
$excludePatterns = @(
    "--exclude=.git",
    "--exclude=venv",
    "--exclude=__pycache__",
    "--exclude=*.pyc",
    "--exclude=*.log",
    "--exclude=logs",
    "--exclude=.vscode",
    "--exclude=.idea",
    "--exclude=.cursor",
    "--exclude=data/data",
    "--exclude=*.db",
    "--exclude=.env",
    "--exclude=.env.local",
    "--exclude=tests",
    "--exclude=pytest.ini"
)

# Если tar доступен в Git Bash
$tarPath = "C:\Program Files\Git\usr\bin\tar.exe"
if (Test-Path $tarPath) {
    & $tarPath -czf $tempArchive $excludePatterns -C $PROJECT_PATH .
    
    Write-Host "📤 Загрузка на VPS..." -ForegroundColor Yellow
    scp $tempArchive "$VPS_USER@${VPS_IP}:$tempArchive"
    
    Write-Host "📦 Распаковка на VPS..." -ForegroundColor Yellow
    ssh "$VPS_USER@$VPS_IP" "tar -xzf $tempArchive -C $VPS_PATH && rm $tempArchive"
    
    # Удаление локального архива
    Remove-Item $tempArchive
    
    Write-Host ""
    Write-Host "✅ Файлы успешно загружены!" -ForegroundColor Green
} else {
    Write-Host "❌ tar не найден! Используйте альтернативный метод:" -ForegroundColor Red
    Write-Host ""
    Write-Host "Вариант 1: Используйте WSL (Windows Subsystem for Linux)" -ForegroundColor Yellow
    Write-Host "Вариант 2: Установите rsync для Windows" -ForegroundColor Yellow
    Write-Host "Вариант 3: Вручную скопируйте нужные файлы" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📋 Следующие шаги:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Подключитесь к VPS:"
Write-Host "   ssh $VPS_USER@$VPS_IP" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Перейдите в папку проекта:"
Write-Host "   cd $VPS_PATH" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Создайте .env.local с токенами:"
Write-Host "   nano .env.local" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Запустите деплой:"
Write-Host "   chmod +x deploy_vps.sh" -ForegroundColor Yellow
Write-Host "   bash deploy_vps.sh" -ForegroundColor Yellow
Write-Host ""



