# Deployment Guide - Holiday Traditions Bot

## Шаг 1: Создание GitHub репозитория

### Вариант A: Через веб-интерфейс GitHub

1. Откройте [github.com/new](https://github.com/new)
2. Заполните форму:
   - **Repository name**: `holiday-traditions-bot`
   - **Description**: `Telegram bot that generates holiday traditions from different countries using AI`
   - **Visibility**: Public или Private (на ваш выбор)
   - **НЕ** ставьте галочки на "Add README" (у нас уже есть)
3. Нажмите "Create repository"

### Вариант B: Через GitHub CLI (если установлен)

```bash
gh repo create holiday-traditions-bot --public --source=. --remote=origin --push
```

### После создания репозитория на GitHub:

Выполните команды (замените YOUR_USERNAME на ваш GitHub username):

```bash
cd /Users/ruslanstepyko/holiday_bot
git remote add origin https://github.com/YOUR_USERNAME/holiday-traditions-bot.git
git push -u origin main
```

Или используйте SSH:

```bash
git remote add origin git@github.com:YOUR_USERNAME/holiday-traditions-bot.git
git push -u origin main
```

---

## Шаг 2: Deployment на сервер

### Опция 1: VPS/Dedicated Server (рекомендуется)

#### Требования к серверу:
- Ubuntu 20.04+ / Debian 11+
- Python 3.8+
- 512 MB RAM минимум
- 1 GB свободного места

#### 1. Подключение к серверу

```bash
ssh user@your-server-ip
```

#### 2. Установка зависимостей

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и pip
sudo apt install python3 python3-pip python3-venv git -y
```

#### 3. Клонирование репозитория

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/holiday-traditions-bot.git
cd holiday-traditions-bot
```

#### 4. Настройка окружения

```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

#### 5. Настройка .env файла

```bash
cp .env.example .env
nano .env
```

Заполните:
```env
TELEGRAM_BOT_TOKEN=ваш_токен
OPENAI_API_KEY=ваш_ключ
OPENAI_MODEL=gpt-4o-mini
```

Сохраните: `Ctrl+X`, затем `Y`, затем `Enter`

#### 6. Тестирование

```bash
python llm.py
# Должно вывести успешное подключение

python bot.py
# Проверьте бота в Telegram
# Остановите: Ctrl+C
```

#### 7. Запуск как systemd сервис (автозапуск)

Создайте файл сервиса:

```bash
sudo nano /etc/systemd/system/holiday-bot.service
```

Вставьте:

```ini
[Unit]
Description=Holiday Traditions Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/holiday-traditions-bot
Environment="PATH=/home/YOUR_USERNAME/holiday-traditions-bot/venv/bin"
ExecStart=/home/YOUR_USERNAME/holiday-traditions-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Замените `YOUR_USERNAME` на ваше имя пользователя на сервере.

Активируйте сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable holiday-bot
sudo systemctl start holiday-bot
```

Проверка статуса:

```bash
sudo systemctl status holiday-bot
```

Просмотр логов:

```bash
sudo journalctl -u holiday-bot -f
```

#### 8. Управление сервисом

```bash
# Остановка
sudo systemctl stop holiday-bot

# Перезапуск
sudo systemctl restart holiday-bot

# Статус
sudo systemctl status holiday-bot

# Логи
sudo journalctl -u holiday-bot -n 100
```

---

### Опция 2: Docker Deployment

#### Создайте Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

#### Создайте docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: holiday-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
```

#### Запуск

```bash
docker-compose up -d
```

---

### Опция 3: Heroku (бесплатный tier закрыт, но можно использовать)

#### 1. Создайте Procfile

```
worker: python bot.py
```

#### 2. Деплой

```bash
heroku create holiday-traditions-bot
heroku config:set TELEGRAM_BOT_TOKEN=ваш_токен
heroku config:set OPENAI_API_KEY=ваш_ключ
heroku config:set OPENAI_MODEL=gpt-4o-mini
git push heroku main
heroku ps:scale worker=1
```

---

### Опция 4: Railway.app (рекомендуется для быстрого деплоя)

1. Зарегистрируйтесь на [railway.app](https://railway.app)
2. Создайте новый проект
3. Подключите GitHub репозиторий
4. Добавьте переменные окружения:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL`
5. Deploy автоматически запустится

---

### Опция 5: DigitalOcean App Platform

1. Зарегистрируйтесь на [DigitalOcean](https://www.digitalocean.com)
2. Создайте App
3. Подключите GitHub репозиторий
4. Выберите тип: Worker
5. Добавьте переменные окружения
6. Deploy

---

## Обновление бота на сервере

### После изменений в коде:

```bash
# На локальном компьютере
git add .
git commit -m "Update: описание изменений"
git push

# На сервере
cd ~/holiday-traditions-bot
git pull
sudo systemctl restart holiday-bot
```

---

## Мониторинг

### Проверка работоспособности

```bash
# Логи в реальном времени
sudo journalctl -u holiday-bot -f

# Последние 100 строк логов
sudo journalctl -u holiday-bot -n 100

# Статус сервиса
sudo systemctl status holiday-bot
```

### Автоматический перезапуск при падении

Systemd сервис автоматически перезапустит бота при падении (настроено через `Restart=always`).

---

## Безопасность

### 1. Firewall

```bash
sudo ufw allow ssh
sudo ufw enable
```

### 2. Обновления

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Защита .env

```bash
chmod 600 .env
```

---

## Troubleshooting

### Бот не запускается

```bash
# Проверьте логи
sudo journalctl -u holiday-bot -n 50

# Проверьте .env файл
cat .env

# Протестируйте вручную
cd ~/holiday-traditions-bot
source venv/bin/activate
python bot.py
```

### Ошибки OpenAI

- Проверьте баланс на [platform.openai.com](https://platform.openai.com)
- Проверьте правильность API ключа

### Telegram не отвечает

- Проверьте токен бота
- Проверьте интернет соединение на сервере

---

## Рекомендуемые провайдеры

| Провайдер | Цена/месяц | Плюсы | Минусы |
|-----------|------------|-------|--------|
| **DigitalOcean** | $4-6 | Простота, надежность | Платный |
| **Railway.app** | $5 (500h бесплатно) | Автодеплой, простота | Лимиты на free tier |
| **Hetzner** | €4-5 | Дешево, мощно | Нет автодеплоя |
| **Linode** | $5 | Хорошая документация | - |
| **Vultr** | $3.50-6 | Много локаций | - |

---

## Следующие шаги

1. Создайте GitHub репозиторий
2. Выберите хостинг провайдер
3. Следуйте инструкциям выше
4. Наслаждайтесь работающимботом 24/7!
