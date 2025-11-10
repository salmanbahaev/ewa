# 🚀 Деплой на VPS (Ubuntu)

## Требования

- Ubuntu 20.04+ VPS
- SSH доступ
- Права sudo

---

## 🎯 Быстрый деплой (рекомендуется)

### Шаг 1: Подключение к VPS и загрузка проекта

```bash
ssh your_user@your_vps_ip
```

**Вариант А: Через Git (если репозиторий настроен)**

```bash
git clone <your_repository_url>
cd ewa
```

**Вариант Б: Через SCP (с локального компа)**

```bash
# НА ЛОКАЛЬНОМ КОМПЕ (в PowerShell/CMD):
scp -r D:\AI_PROJECTS\ewa your_user@your_vps_ip:~/

# Затем НА VPS:
ssh your_user@your_vps_ip
cd ~/ewa
```

---

### Шаг 2: Создайте .env.local с токенами

```bash
nano .env.local
```

Вставьте ваши токены:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
OPENAI_API_KEY=ваш_openai_api_ключ
OPENAI_MODEL=gpt-4o-mini
DATABASE_PATH=data/bot_database.db
LOG_LEVEL=INFO
LOG_DIR=logs
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

---

### Шаг 3: Запустите скрипт автоматического деплоя

```bash
chmod +x deploy_vps.sh
bash deploy_vps.sh
```

**Скрипт автоматически:**

- ✅ Установит Python (если нужно)
- ✅ Создаст виртуальное окружение
- ✅ Установит зависимости
- ✅ Настроит systemd service
- ✅ Включит автозапуск
- ✅ Запустит бота

---

### ✅ Готово!

Бот работает 24/7 с:

- 🔄 Автоматическим перезапуском при падении (каждые 10 сек)
- 🚀 Автозапуском при перезагрузке сервера
- 🛡️ Защитой от бесконечного цикла перезапусков
- 💾 Ограничением памяти (512MB) и CPU (50%)

---

## 📋 Ручной деплой (опционально)

<details>
<summary>Развернуть инструкцию ручного деплоя</summary>

### Шаг 1: Установка Python и зависимостей

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
python3 --version
```

### Шаг 2: Настройка проекта

```bash
cd ~/ewa
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Шаг 3: Тестовый запуск

```bash
python3 main.py
# Проверьте бота в Telegram
# Ctrl+C для остановки
```

### Шаг 4: Создание systemd service

```bash
sudo nano /etc/systemd/system/ewa-bot.service
```

Вставьте (замените `YOUR_USERNAME` на ваш username):

```ini
[Unit]
Description=EWA Product Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/ewa
ExecStart=/home/YOUR_USERNAME/ewa/venv/bin/python /home/YOUR_USERNAME/ewa/main.py

# Автоперезапуск
Restart=always
RestartSec=10

# Ограничения на перезапуски
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
```

### Шаг 5: Запуск

```bash
sudo systemctl daemon-reload
sudo systemctl enable ewa-bot
sudo systemctl start ewa-bot
sudo systemctl status ewa-bot
```

</details>

---

## Управление ботом

### Просмотр логов:

```bash
# Последние логи
sudo journalctl -u ewa-bot -n 50

# Следить за логами в реальном времени
sudo journalctl -u ewa-bot -f
```

### Остановка бота:

```bash
sudo systemctl stop ewa-bot
```

### Перезапуск бота:

```bash
sudo systemctl restart ewa-bot
```

### Отключение автозапуска:

```bash
sudo systemctl disable ewa-bot
```

---

## Обновление бота

```bash
cd ~/ewa

# Остановка бота
sudo systemctl stop ewa-bot

# Обновление кода (если через Git)
git pull

# Обновление зависимостей
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Запуск бота
sudo systemctl start ewa-bot

# Проверка
sudo systemctl status ewa-bot
```

---

## Проблемы и решения

### Бот не запускается

1. **Проверьте логи:**

```bash
sudo journalctl -u ewa-bot -n 100
```

2. **Проверьте `.env.local`:**

```bash
cat ~/ewa/.env.local
```

3. **Проверьте права:**

```bash
ls -la ~/ewa
chmod +x ~/ewa/main.py
```

### Бот падает

Systemd автоматически перезапустит (RestartSec=10).  
Проверьте логи для выяснения причины.

### OpenAI ошибки

- Проверьте баланс на аккаунте OpenAI
- Убедитесь что API ключ активен

---

## Безопасность

1. **Файервол:**

```bash
sudo ufw allow OpenSSH
sudo ufw enable
```

2. **Обновления:**

```bash
sudo apt update && sudo apt upgrade -y
```

3. **Защита .env:**

```bash
chmod 600 ~/ewa/.env.local
```

---

## Готово! 🎉

Ваш бот работает 24/7 на VPS с автоматическим перезапуском при сбоях.
