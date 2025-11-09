# Быстрый деплой на сервер

## Вариант 1: Автоматический деплой (рекомендуется)

### На вашем сервере выполните:

```bash
# 1. Подключитесь к серверу
ssh user@your-server-ip

# 2. Установите Git (если нет)
sudo apt update && sudo apt install git python3 python3-pip python3-venv -y

# 3. Клонируйте репозиторий
git clone https://github.com/seoshmeo/holiday_bot.git
cd holiday_bot

# 4. Запустите автоматический деплой
./deploy.sh
```

Скрипт автоматически:
- Создаст виртуальное окружение
- Установит зависимости
- Проверит конфигурацию
- Предложит выбрать режим запуска

### Заполните .env файл:

```bash
nano .env
```

Вставьте ваши токены:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_botfather
OPENAI_API_KEY=your_openai_api_key_from_platform
OPENAI_MODEL=gpt-4o-mini
```

Сохраните: `Ctrl+X` → `Y` → `Enter`

---

## Вариант 2: Docker (самый простой)

```bash
# На сервере
git clone https://github.com/seoshmeo/holiday_bot.git
cd holiday_bot

# Создайте .env файл
nano .env
# (вставьте токены как выше)

# Запустите через Docker
docker-compose up -d

# Проверка логов
docker-compose logs -f
```

---

## Вариант 3: Systemd сервис (для автозапуска)

```bash
# Клонируйте и настройте
git clone https://github.com/seoshmeo/holiday_bot.git
cd holiday_bot

# Создайте venv и установите зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Создайте .env
cp .env.example .env
nano .env
# (вставьте токены)

# Установите сервис
sudo cp holiday-bot.service /etc/systemd/system/
# Отредактируйте пути в файле:
sudo nano /etc/systemd/system/holiday-bot.service
# Замените YOUR_USERNAME на ваше имя пользователя

# Запустите сервис
sudo systemctl daemon-reload
sudo systemctl enable holiday-bot
sudo systemctl start holiday-bot

# Проверка
sudo systemctl status holiday-bot
```

---

## Управление ботом

### Systemd команды:
```bash
sudo systemctl status holiday-bot    # статус
sudo systemctl restart holiday-bot   # перезапуск
sudo systemctl stop holiday-bot      # остановка
sudo journalctl -u holiday-bot -f    # логи
```

### Docker команды:
```bash
docker-compose ps                    # статус
docker-compose restart               # перезапуск
docker-compose down                  # остановка
docker-compose logs -f               # логи
```

---

## Рекомендуемые VPS провайдеры

### Бюджетные:
- **Hetzner Cloud** - €4/мес (лучшая цена/качество)
- **DigitalOcean** - $6/мес (самый простой)
- **Vultr** - $3.50/мес

### Для начала:
1. Зарегистрируйтесь на [Hetzner](https://www.hetzner.com/cloud)
2. Создайте сервер:
   - Образ: Ubuntu 22.04
   - Тип: CX11 (2GB RAM) - €4/мес
   - Локация: ближайшая к вам
3. Скопируйте IP адрес
4. Подключитесь: `ssh root@your-ip`
5. Следуйте инструкциям выше

---

## Проверка работы

После деплоя:
1. Откройте Telegram
2. Найдите вашего бота: @holiday_country_bot
3. Отправьте `/start`
4. Отправьте `/holiday`
5. Наслаждайтесь!

---

## Обновление бота

```bash
cd holiday_bot
git pull
sudo systemctl restart holiday-bot  # для systemd
# или
docker-compose restart               # для Docker
```

---

## Помощь

Если что-то не работает:

1. Проверьте логи:
   ```bash
   sudo journalctl -u holiday-bot -n 50
   ```

2. Проверьте .env файл:
   ```bash
   cat .env
   ```

3. Протестируйте вручную:
   ```bash
   source venv/bin/activate
   python llm.py
   python bot.py
   ```

---

## Полная документация

Подробная документация: [DEPLOYMENT.md](DEPLOYMENT.md)
