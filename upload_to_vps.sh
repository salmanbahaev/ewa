#!/bin/bash
# Скрипт для загрузки проекта на VPS (только нужные файлы)

# Настройки (измени под себя)
VPS_USER="root"
VPS_IP="193.168.46.189"
VPS_PATH="/root/ewa"
LOCAL_PATH="."

echo "=========================================="
echo "📤 Загрузка EWA Bot на VPS"
echo "=========================================="
echo ""
echo "VPS: $VPS_USER@$VPS_IP"
echo "Путь: $VPS_PATH"
echo ""

# Проверка rsync
if ! command -v rsync &> /dev/null; then
    echo "❌ rsync не установлен!"
    echo "Установите: choco install rsync (Windows) или apt install rsync (Linux)"
    exit 1
fi

# Подтверждение
read -p "Продолжить загрузку? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Отменено"
    exit 0
fi

echo ""
echo "🔄 Очистка старой папки на VPS..."
ssh $VPS_USER@$VPS_IP "rm -rf $VPS_PATH"

echo "📦 Загрузка файлов..."
rsync -avz --progress \
    --exclude-from='.rsyncignore' \
    --exclude='.rsyncignore' \
    --exclude='upload_to_vps.sh' \
    $LOCAL_PATH/ $VPS_USER@$VPS_IP:$VPS_PATH/

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Файлы успешно загружены!"
    echo ""
    echo "=========================================="
    echo "📋 Следующие шаги:"
    echo "=========================================="
    echo ""
    echo "1. Подключитесь к VPS:"
    echo "   ssh $VPS_USER@$VPS_IP"
    echo ""
    echo "2. Перейдите в папку проекта:"
    echo "   cd $VPS_PATH"
    echo ""
    echo "3. Создайте .env.local с токенами:"
    echo "   nano .env.local"
    echo ""
    echo "4. Запустите деплой:"
    echo "   chmod +x deploy_vps.sh"
    echo "   bash deploy_vps.sh"
    echo ""
else
    echo ""
    echo "❌ Ошибка при загрузке!"
    exit 1
fi



