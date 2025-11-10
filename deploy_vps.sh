#!/bin/bash
# Скрипт автоматического деплоя EWA Bot на VPS
# Запуск: bash deploy_vps.sh

set -e

echo "=========================================="
echo "🚀 Деплой EWA Product Telegram Bot"
echo "=========================================="
echo ""

# Проверка Python
echo "📦 Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен. Установка..."
    sudo apt update
    sudo apt install python3 python3-pip python3-venv -y
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION установлен"
echo ""

# Получение текущего пользователя и директории
CURRENT_USER=$(whoami)
BOT_DIR=$(pwd)

echo "👤 Пользователь: $CURRENT_USER"
echo "📁 Директория: $BOT_DIR"
echo ""

# Создание виртуального окружения
echo "🔧 Настройка виртуального окружения..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Виртуальное окружение создано"
else
    echo "✅ Виртуальное окружение уже существует"
fi

# Активация и установка зависимостей
source venv/bin/activate
echo "📥 Установка зависимостей..."
pip install -r requirements.txt --quiet
echo "✅ Зависимости установлены"
echo ""

# Проверка .env файла
echo "🔑 Проверка конфигурации..."
if [ ! -f ".env.local" ] && [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден!"
    echo "Создайте .env.local с токенами:"
    echo ""
    echo "TELEGRAM_BOT_TOKEN=ваш_токен"
    echo "OPENAI_API_KEY=ваш_ключ"
    echo ""
    read -p "Хотите создать сейчас? (y/n): " create_env
    if [ "$create_env" = "y" ]; then
        read -p "Telegram Bot Token: " bot_token
        read -p "OpenAI API Key: " openai_key
        cat > .env.local << EOF
TELEGRAM_BOT_TOKEN=$bot_token
OPENAI_API_KEY=$openai_key
OPENAI_MODEL=gpt-4o-mini
DATABASE_PATH=data/bot_database.db
LOG_LEVEL=INFO
LOG_DIR=logs
EOF
        chmod 600 .env.local
        echo "✅ Конфигурация создана"
    else
        echo "❌ Создайте .env.local вручную и запустите скрипт снова"
        exit 1
    fi
else
    echo "✅ Конфигурация найдена"
fi
echo ""

# Создание systemd service
echo "⚙️  Настройка systemd service..."
SERVICE_FILE="/etc/systemd/system/ewa-bot.service"

sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=EWA Product Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$BOT_DIR
ExecStart=$BOT_DIR/venv/bin/python $BOT_DIR/main.py

# Автоперезапуск
Restart=always
RestartSec=10

# Ограничения на перезапуски (защита от бесконечного цикла)
StartLimitInterval=300
StartLimitBurst=5

# Environment
Environment="PYTHONUNBUFFERED=1"

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ewa-bot

# Безопасность и ресурсы
Nice=0
CPUQuota=50%
MemoryLimit=512M

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service файл создан: $SERVICE_FILE"
echo ""

# Активация и запуск
echo "🚀 Запуск бота..."
sudo systemctl daemon-reload
sudo systemctl enable ewa-bot
sudo systemctl restart ewa-bot

# Ожидание запуска
sleep 3

# Проверка статуса
if sudo systemctl is-active --quiet ewa-bot; then
    echo "✅ Бот успешно запущен!"
    echo ""
    echo "=========================================="
    echo "✨ Деплой завершён успешно!"
    echo "=========================================="
    echo ""
    echo "📊 Управление ботом:"
    echo "   sudo systemctl status ewa-bot    # Статус"
    echo "   sudo systemctl restart ewa-bot   # Перезапуск"
    echo "   sudo systemctl stop ewa-bot      # Остановка"
    echo "   sudo journalctl -u ewa-bot -f    # Логи в реальном времени"
    echo ""
else
    echo "❌ Ошибка запуска бота!"
    echo "Проверьте логи: sudo journalctl -u ewa-bot -n 50"
    exit 1
fi

