# ⚡ Быстрый деплой на VPS

## 3 простых шага

### 1️⃣ Загрузите проект на VPS

```bash
# На локальном компе:
scp -r D:\AI_PROJECTS\ewa your_user@your_vps_ip:~/

# На VPS:
ssh your_user@your_vps_ip
cd ~/ewa
```

---

### 2️⃣ Создайте .env.local

```bash
nano .env.local
```

Вставьте:
```env
TELEGRAM_BOT_TOKEN=ваш_токен
OPENAI_API_KEY=ваш_ключ
OPENAI_MODEL=gpt-4o-mini
DATABASE_PATH=data/bot_database.db
LOG_LEVEL=INFO
LOG_DIR=logs
```

---

### 3️⃣ Запустите

```bash
chmod +x deploy_vps.sh
bash deploy_vps.sh
```

**Готово! Бот работает 24/7** 🎉

---

## Управление

```bash
sudo systemctl status ewa-bot      # Статус
sudo systemctl restart ewa-bot     # Перезапуск
sudo systemctl stop ewa-bot        # Остановка
sudo journalctl -u ewa-bot -f      # Логи (реал-тайм)
sudo journalctl -u ewa-bot -n 100  # Последние 100 строк
```

---

## Что настроено автоматически

✅ **Автозапуск** при загрузке сервера  
✅ **Автоперезапуск** при падении (через 10 сек)  
✅ **Защита** от бесконечных перезапусков (макс 5 за 5 минут)  
✅ **Лимиты** ресурсов (512MB RAM, 50% CPU)  
✅ **Логирование** в systemd journal  

---

## Проверка работы

```bash
# Проверка статуса
sudo systemctl status ewa-bot

# Если активен (active (running)) - всё ОК! ✅
```

---

## При проблемах

```bash
# Смотрим логи
sudo journalctl -u ewa-bot -n 50

# Проверяем .env.local
cat .env.local

# Перезапускаем
sudo systemctl restart ewa-bot
```

---

## Обновление бота

```bash
cd ~/ewa
sudo systemctl stop ewa-bot
git pull  # или загрузите новые файлы через scp
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl start ewa-bot
```



