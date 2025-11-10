# 📤 Ручная загрузка на VPS (простой способ)

## Вариант 1: Через SCP - только нужные папки

```powershell
# В PowerShell на Windows

# 1. Очистить старую папку на VPS
ssh root@193.168.46.189 "rm -rf /root/ewa && mkdir -p /root/ewa"

# 2. Копировать только нужные файлы и папки

# Основные файлы
scp D:\AI_PROJECTS\ewa\main.py root@193.168.46.189:/root/ewa/
scp D:\AI_PROJECTS\ewa\config.py root@193.168.46.189:/root/ewa/
scp D:\AI_PROJECTS\ewa\requirements.txt root@193.168.46.189:/root/ewa/
scp D:\AI_PROJECTS\ewa\deploy_vps.sh root@193.168.46.189:/root/ewa/

# Папка bot (обработчики бота)
scp -r D:\AI_PROJECTS\ewa\bot root@193.168.46.189:/root/ewa/

# Папка ai (AI логика)
scp -r D:\AI_PROJECTS\ewa\ai root@193.168.46.189:/root/ewa/

# Папка data (JSON файлы и database.py)
scp -r D:\AI_PROJECTS\ewa\data root@193.168.46.189:/root/ewa/

# Документация (опционально)
scp D:\AI_PROJECTS\ewa\DEPLOY.md root@193.168.46.189:/root/ewa/
scp D:\AI_PROJECTS\ewa\DEPLOY_QUICK.md root@193.168.46.189:/root/ewa/
scp D:\AI_PROJECTS\ewa\README.md root@193.168.46.189:/root/ewa/
```

---

## Вариант 2: Через архив (самый чистый)

```powershell
# В PowerShell на Windows

# 1. Создать временную папку для чистых файлов
cd D:\AI_PROJECTS\
New-Item -ItemType Directory -Path "ewa_clean" -Force

# 2. Скопировать только нужные файлы
Copy-Item -Path "ewa\main.py" -Destination "ewa_clean\"
Copy-Item -Path "ewa\config.py" -Destination "ewa_clean\"
Copy-Item -Path "ewa\requirements.txt" -Destination "ewa_clean\"
Copy-Item -Path "ewa\deploy_vps.sh" -Destination "ewa_clean\"
Copy-Item -Path "ewa\bot" -Destination "ewa_clean\bot" -Recurse
Copy-Item -Path "ewa\ai" -Destination "ewa_clean\ai" -Recurse
Copy-Item -Path "ewa\data" -Destination "ewa_clean\data" -Recurse

# 3. Удалить __pycache__ из копии
Get-ChildItem -Path "ewa_clean" -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# 4. Загрузить на VPS
scp -r ewa_clean root@193.168.46.189:/root/ewa_temp

# 5. На VPS переместить файлы
ssh root@193.168.46.189 "rm -rf /root/ewa && mv /root/ewa_temp /root/ewa"

# 6. Удалить временную папку локально
Remove-Item -Path "ewa_clean" -Recurse -Force
```

---

## Вариант 3: Используй готовый PowerShell скрипт

Измени IP и пути в `upload_to_vps.ps1`, затем:

```powershell
.\upload_to_vps.ps1
```

---

## ✅ Что должно быть на VPS после загрузки:

```
/root/ewa/
├── main.py
├── config.py
├── requirements.txt
├── deploy_vps.sh
├── bot/
│   ├── __init__.py
│   ├── handlers/
│   ├── keyboards/
│   └── middlewares/
├── ai/
│   ├── __init__.py
│   ├── assistant.py
│   ├── prompts.py
│   └── product_search.py
└── data/
    ├── __init__.py
    ├── database.py
    ├── catalog.json
    ├── company.json
    ├── business.json
    ├── events.json
    └── geography.json
```

❌ **НЕ должно быть:**
- `.git/`
- `venv/`
- `__pycache__/`
- `logs/`
- `.env` или `.env.local` (создашь на VPS)
- `tests/`

---

## 🚀 После загрузки:

```bash
# Подключиться к VPS
ssh root@193.168.46.189

# Проверить файлы
ls -la /root/ewa

# Перейти в папку
cd /root/ewa

# Создать .env.local
nano .env.local
```

Вставь:
```env
TELEGRAM_BOT_TOKEN=твой_токен
OPENAI_API_KEY=твой_ключ
OPENAI_MODEL=gpt-4o-mini
DATABASE_PATH=data/bot_database.db
LOG_LEVEL=INFO
LOG_DIR=logs
```

```bash
# Запустить деплой
chmod +x deploy_vps.sh
bash deploy_vps.sh
```



