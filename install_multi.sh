#!/bin/bash

# Скрипт для установки Holiday Bot на сервер с несколькими ботами
# Полная изоляция - своя папка, свой venv, свой systemd сервис

set -e  # Остановка при ошибке

echo "🎄 Holiday Bot - Установка на мульти-бот сервер"
echo "================================================"
echo ""

# Определяем текущего пользователя
CURRENT_USER=$(whoami)
echo "👤 Пользователь: $CURRENT_USER"

# Запрашиваем путь установки
echo ""
echo "📂 Куда установить бота?"
read -p "Путь (по умолчанию: ~/bots/holiday_bot): " INSTALL_PATH
INSTALL_PATH=${INSTALL_PATH:-~/bots/holiday_bot}

# Раскрываем ~
INSTALL_PATH=$(eval echo "$INSTALL_PATH")

echo "📍 Путь установки: $INSTALL_PATH"

# Проверяем, существует ли уже папка
if [ -d "$INSTALL_PATH" ]; then
    echo "⚠️  Папка уже существует: $INSTALL_PATH"
    read -p "Удалить и переустановить? (y/n): " REINSTALL
    if [ "$REINSTALL" = "y" ]; then
        echo "🗑️  Удаляем старую папку..."
        rm -rf "$INSTALL_PATH"
    else
        echo "❌ Установка отменена"
        exit 1
    fi
fi

# Создаем родительскую директорию
PARENT_DIR=$(dirname "$INSTALL_PATH")
mkdir -p "$PARENT_DIR"

echo ""
echo "📥 Клонирование репозитория..."
git clone https://github.com/seoshmeo/holiday_bot.git "$INSTALL_PATH"

cd "$INSTALL_PATH"

echo ""
echo "🐍 Создание виртуального окружения..."
python3 -m venv venv

echo "📦 Установка зависимостей..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "⚙️  Настройка .env файла..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Файл .env создан"

    echo ""
    echo "📝 Введите токены:"
    echo ""

    # Telegram токен
    read -p "Telegram Bot Token: " TG_TOKEN
    if [ -n "$TG_TOKEN" ]; then
        sed -i.bak "s|TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=$TG_TOKEN|" .env
    fi

    # OpenAI токен
    read -p "OpenAI API Key: " OPENAI_KEY
    if [ -n "$OPENAI_KEY" ]; then
        sed -i.bak "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_KEY|" .env
    fi

    # Удаляем backup файлы
    rm -f .env.bak

    echo "✅ Токены сохранены"
else
    echo "ℹ️  Файл .env уже существует, пропускаем"
fi

echo ""
echo "🧪 Тестирование подключения..."

# Тест OpenAI
if python llm.py 2>&1 | grep -q "Подключение успешно"; then
    echo "✅ OpenAI подключение OK"
else
    echo "⚠️  Проблема с OpenAI. Проверьте .env файл позже"
fi

echo ""
echo "🔧 Настройка systemd сервиса..."

# Генерируем уникальное имя сервиса
SERVICE_NAME="holiday-traditions-bot"

# Проверяем, не занято ли имя
if systemctl list-units --full --all | grep -q "$SERVICE_NAME.service"; then
    echo "⚠️  Сервис $SERVICE_NAME уже существует"
    read -p "Введите уникальное имя сервиса (например, holiday-bot-2): " CUSTOM_NAME
    if [ -n "$CUSTOM_NAME" ]; then
        SERVICE_NAME="$CUSTOM_NAME"
    fi
fi

echo "📝 Имя сервиса: $SERVICE_NAME"

# Создаем файл сервиса
SERVICE_FILE="/tmp/$SERVICE_NAME.service"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Holiday Traditions Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_PATH
Environment="PATH=$INSTALL_PATH/venv/bin"
ExecStart=$INSTALL_PATH/venv/bin/python bot.py
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_PATH/bot.log
StandardError=append:$INSTALL_PATH/bot_error.log

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "🔐 Установка сервиса (требуются sudo права)..."

# Копируем и активируем сервис
sudo cp "$SERVICE_FILE" "/etc/systemd/system/$SERVICE_NAME.service"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

echo ""
read -p "🚀 Запустить бота сейчас? (y/n): " START_NOW

if [ "$START_NOW" = "y" ]; then
    sudo systemctl start "$SERVICE_NAME"
    sleep 2

    echo ""
    echo "📊 Статус бота:"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l

    echo ""
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "✅ Бот успешно запущен!"
    else
        echo "❌ Бот не запустился. Проверьте логи:"
        echo "   sudo journalctl -u $SERVICE_NAME -n 50"
    fi
else
    echo "ℹ️  Бот не запущен. Для запуска используйте:"
    echo "   sudo systemctl start $SERVICE_NAME"
fi

echo ""
echo "================================================"
echo "🎉 Установка завершена!"
echo "================================================"
echo ""
echo "📂 Папка бота: $INSTALL_PATH"
echo "🔧 Имя сервиса: $SERVICE_NAME"
echo ""
echo "📋 Команды управления:"
echo "   sudo systemctl status $SERVICE_NAME     # статус"
echo "   sudo systemctl restart $SERVICE_NAME    # перезапуск"
echo "   sudo systemctl stop $SERVICE_NAME       # остановка"
echo "   sudo journalctl -u $SERVICE_NAME -f     # логи"
echo ""
echo "📝 Файлы логов:"
echo "   $INSTALL_PATH/bot.log        # основной лог"
echo "   $INSTALL_PATH/bot_error.log  # лог ошибок"
echo ""
echo "🔄 Для обновления бота:"
echo "   cd $INSTALL_PATH"
echo "   git pull"
echo "   sudo systemctl restart $SERVICE_NAME"
echo ""
echo "✨ Готово! Бот изолирован от других ботов на сервере."
