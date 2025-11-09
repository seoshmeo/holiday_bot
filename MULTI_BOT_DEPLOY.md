# Деплой на сервер с несколькими ботами

## Изолированная установка

Эта инструкция покажет, как установить Holiday Bot на сервер, где уже работают другие боты, без конфликтов.

---

## Шаг 1: Подключение к серверу

```bash
ssh user@your-server-ip
```

---

## Шаг 2: Создание отдельной директории

```bash
# Переходим в домашнюю директорию
cd ~

# Создаем папку для ботов (если её нет)
mkdir -p bots

# Клонируем в отдельную папку
git clone https://github.com/seoshmeo/holiday_bot.git ~/bots/holiday_bot
cd ~/bots/holiday_bot
```

**Структура будет:**
```
/home/user/
├── bots/
│   ├── holiday_bot/          # Ваш новый бот
│   ├── other_bot_1/          # Другие боты
│   └── other_bot_2/
```

---

## Шаг 3: Создание изолированного виртуального окружения

```bash
cd ~/bots/holiday_bot

# Создаем ОТДЕЛЬНОЕ виртуальное окружение
python3 -m venv venv

# Активируем
source venv/bin/activate

# Устанавливаем зависимости только для этого бота
pip install -r requirements.txt
```

**Важно**: У каждого бота будет свой `venv`, поэтому нет конфликтов библиотек!

---

## Шаг 4: Настройка .env файла

```bash
# Создаем .env из примера
cp .env.example .env

# Редактируем
nano .env
```

Вставьте токены:
```env
TELEGRAM_BOT_TOKEN=7784405747:AAEUDA60YNrtWaeOMGL2koNqSyADySClvzE
OPENAI_API_KEY=sk-proj-ваш_ключ
OPENAI_MODEL=gpt-4o-mini
```

Сохраните: `Ctrl+X` → `Y` → `Enter`

---

## Шаг 5: Тестирование

```bash
# Активируем окружение (если не активировано)
source venv/bin/activate

# Тестируем LLM
python llm.py

# Если все ОК, тестируем бота (Ctrl+C для остановки)
python bot.py
```

---

## Шаг 6: Создание изолированного systemd сервиса

### Вариант A: Уникальное имя сервиса

```bash
# Получаем текущего пользователя и директорию
CURRENT_USER=$(whoami)
BOT_DIR="$HOME/bots/holiday_bot"

# Создаем файл сервиса с УНИКАЛЬНЫМ именем
sudo nano /etc/systemd/system/holiday-traditions-bot.service
```

Вставьте (замените YOUR_USERNAME на ваше имя пользователя):

```ini
[Unit]
Description=Holiday Traditions Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/bots/holiday_bot
Environment="PATH=/home/YOUR_USERNAME/bots/holiday_bot/venv/bin"
ExecStart=/home/YOUR_USERNAME/bots/holiday_bot/venv/bin/python bot.py
Restart=always
RestartSec=10
StandardOutput=append:/home/YOUR_USERNAME/bots/holiday_bot/bot.log
StandardError=append:/home/YOUR_USERNAME/bots/holiday_bot/bot_error.log

[Install]
WantedBy=multi-user.target
```

### Вариант B: Автоматическое создание сервиса

```bash
cd ~/bots/holiday_bot

# Используем встроенный скрипт
./deploy.sh
# Выберите опцию 3 (Install as systemd service)
```

---

## Шаг 7: Активация сервиса

```bash
# Перезагрузка конфигурации systemd
sudo systemctl daemon-reload

# Включить автозапуск
sudo systemctl enable holiday-traditions-bot

# Запустить сейчас
sudo systemctl start holiday-traditions-bot

# Проверить статус
sudo systemctl status holiday-traditions-bot
```

---

## Управление ботом

### Основные команды:

```bash
# Статус
sudo systemctl status holiday-traditions-bot

# Перезапуск
sudo systemctl restart holiday-traditions-bot

# Остановка
sudo systemctl stop holiday-traditions-bot

# Просмотр логов в реальном времени
sudo journalctl -u holiday-traditions-bot -f

# Последние 50 строк логов
sudo journalctl -u holiday-traditions-bot -n 50
```

### Логи в файлах:

```bash
# Обычные логи
tail -f ~/bots/holiday_bot/bot.log

# Логи ошибок
tail -f ~/bots/holiday_bot/bot_error.log
```

---

## Вариант с Docker (еще проще!)

Если у вас установлен Docker, это самый изолированный способ:

```bash
cd ~/bots/holiday_bot

# Создайте .env файл
nano .env
# (вставьте токены)

# Запустите через Docker
docker-compose up -d

# Проверка
docker-compose ps
docker-compose logs -f
```

**Преимущества Docker:**
- Полная изоляция от других ботов
- Нет конфликтов библиотек
- Легко обновлять и откатывать

---

## Проверка портов и конфликтов

Telegram боты не используют порты (работают через long polling), поэтому:

✅ **Нет конфликтов по портам**
✅ **Можно запускать неограниченное количество ботов**
✅ **Каждый бот работает независимо**

---

## Список всех ботов на сервере

### Посмотреть все systemd сервисы ботов:

```bash
systemctl list-units --type=service | grep bot
```

### Посмотреть все папки с ботами:

```bash
ls -la ~/bots/
```

### Посмотреть все Docker контейнеры:

```bash
docker ps
```

---

## Обновление бота

```bash
cd ~/bots/holiday_bot

# Остановить бот
sudo systemctl stop holiday-traditions-bot

# Обновить код
git pull

# Обновить зависимости (если изменились)
source venv/bin/activate
pip install -r requirements.txt

# Запустить снова
sudo systemctl start holiday-traditions-bot

# Проверить
sudo systemctl status holiday-traditions-bot
```

---

## Структура файлов

После установки у вас будет:

```
/home/user/
├── bots/
│   ├── holiday_bot/
│   │   ├── venv/              # Изолированное окружение
│   │   ├── bot.py
│   │   ├── llm.py
│   │   ├── .env               # Токены (НЕ в git)
│   │   ├── bot.log            # Логи
│   │   └── bot_error.log      # Логи ошибок
│   ├── other_bot_1/
│   │   └── venv/              # Своё окружение
│   └── other_bot_2/
│       └── venv/              # Своё окружение
```

---

## Мониторинг ресурсов

### Проверить использование памяти всеми ботами:

```bash
ps aux | grep python | grep bot
```

### Проверить использование диска:

```bash
du -sh ~/bots/*
```

### Проверить системные ресурсы:

```bash
htop
# или
top
```

---

## Автоматический рестарт при перезагрузке сервера

Systemd автоматически запустит бота после перезагрузки, если вы выполнили:

```bash
sudo systemctl enable holiday-traditions-bot
```

Проверить автозагрузку:

```bash
systemctl is-enabled holiday-traditions-bot
# Должно вывести: enabled
```

---

## Удаление бота (если понадобится)

```bash
# Остановить и отключить сервис
sudo systemctl stop holiday-traditions-bot
sudo systemctl disable holiday-traditions-bot

# Удалить файл сервиса
sudo rm /etc/systemd/system/holiday-traditions-bot.service
sudo systemctl daemon-reload

# Удалить папку с ботом
rm -rf ~/bots/holiday_bot
```

---

## Резюме преимуществ этого подхода

✅ **Полная изоляция** - каждый бот в своей папке
✅ **Нет конфликтов библиотек** - отдельный venv
✅ **Уникальное имя сервиса** - holiday-traditions-bot
✅ **Отдельные логи** - легко отлаживать
✅ **Автозапуск** - работает после перезагрузки
✅ **Легко обновлять** - git pull
✅ **Можно добавлять неограниченное количество ботов**

---

## Быстрая команда для полного деплоя

Скопируйте и выполните одной командой (замените YOUR_USERNAME):

```bash
cd ~ && \
mkdir -p bots && \
cd bots && \
git clone https://github.com/seoshmeo/holiday_bot.git && \
cd holiday_bot && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
cp .env.example .env && \
echo "✅ Установка завершена! Теперь отредактируйте .env файл:" && \
echo "nano .env"
```

После этого:
1. Отредактируйте `.env`
2. Запустите `./deploy.sh` и выберите опцию 3

---

## Поддержка

Если возникли проблемы:

1. Проверьте логи: `sudo journalctl -u holiday-traditions-bot -n 50`
2. Проверьте статус: `sudo systemctl status holiday-traditions-bot`
3. Проверьте .env файл: `cat .env`
4. Проверьте права: `ls -la ~/bots/holiday_bot`

---

**Готово! Ваш бот будет работать изолированно от других ботов на сервере.**
