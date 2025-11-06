# 🚀 Деплой на VPS (Ubuntu)

## Требования

- Ubuntu 20.04+ VPS
- SSH доступ
- Права sudo

---

## Шаг 1: Подключение к VPS

```bash
ssh your_user@your_vps_ip
```

---

## Шаг 2: Установка Python и зависимостей

```bash
# Обновление системы
sudo apt update
sudo apt upgrade -y

# Установка Python 3.10+
sudo apt install python3 python3-pip python3-venv git -y

# Проверка версии
python3 --version
```

---

## Шаг 3: Загрузка проекта

**Вариант 1: Через Git**

```bash
git clone <your_repository_url>
cd ewa
```

**Вариант 2: Через SCP (локально)**

```bash
# На вашем компе
scp -r D:\CURSOR_PROJECTS\ewa your_user@your_vps_ip:~/
```

---

## Шаг 4: Настройка проекта

```bash
cd ~/ewa

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

---

## Шаг 5: Конфигурация

Создайте `.env.local`:

```bash
nano .env.local
```

Вставьте:

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

## Шаг 6: Тестовый запуск

```bash
python3 main.py
```

Проверьте что бот работает в Telegram.  
Остановите: `Ctrl+C`

---

## Шаг 7: Создание systemd service

```bash
sudo nano /etc/systemd/system/ewa-bot.service
```

Вставьте (замените `YOUR_USERNAME` и пути):

```ini
[Unit]
Description=EWA Product Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/ewa
ExecStart=/home/YOUR_USERNAME/ewa/venv/bin/python /home/YOUR_USERNAME/ewa/main.py
Restart=always
RestartSec=10

# Environment
Environment="PYTHONUNBUFFERED=1"

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## Шаг 8: Запуск сервиса

```bash
# Перезагрузка конфигурации systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable ewa-bot

# Запуск бота
sudo systemctl start ewa-bot

# Проверка статуса
sudo systemctl status ewa-bot
```

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
