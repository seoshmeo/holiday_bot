#!/bin/bash

# Скрипт для деплоя Holiday Bot на VPS/сервер

echo "🚀 Holiday Bot Deployment Script"
echo "=================================="

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

echo "✅ Python найден: $(python3 --version)"

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install -r requirements.txt

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден!"
    echo "📝 Создание .env из примера..."
    cp .env.example .env
    echo "❗ Пожалуйста, отредактируйте .env файл и добавьте токены:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - OPENAI_API_KEY"
    echo ""
    echo "После редактирования запустите скрипт снова."
    exit 1
fi

echo "✅ Файл .env найден"

# Тестирование подключения
echo "🧪 Тестирование подключения к OpenAI..."
python llm.py

if [ $? -eq 0 ]; then
    echo "✅ Тест успешен!"
else
    echo "❌ Тест не прошел. Проверьте .env файл"
    exit 1
fi

# Спросить, запустить ли бота
echo ""
echo "Бот готов к запуску!"
echo "Выберите режим:"
echo "1) Запустить в фоне (background)"
echo "2) Запустить в терминале (foreground)"
echo "3) Установить как systemd сервис"
echo "4) Выход"

read -p "Ваш выбор [1-4]: " choice

case $choice in
    1)
        echo "🚀 Запуск в фоне..."
        nohup python bot.py > bot.log 2>&1 &
        echo "✅ Бот запущен! PID: $!"
        echo "📋 Логи: tail -f bot.log"
        ;;
    2)
        echo "🚀 Запуск бота..."
        python bot.py
        ;;
    3)
        echo "⚙️  Установка systemd сервиса..."

        # Получить текущего пользователя и директорию
        CURRENT_USER=$(whoami)
        CURRENT_DIR=$(pwd)

        # Создать временный файл сервиса
        cat > /tmp/holiday-bot.service << EOF
[Unit]
Description=Holiday Traditions Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/python bot.py
Restart=always
RestartSec=10
StandardOutput=append:$CURRENT_DIR/bot.log
StandardError=append:$CURRENT_DIR/bot_error.log

[Install]
WantedBy=multi-user.target
EOF

        # Копировать и активировать сервис
        sudo cp /tmp/holiday-bot.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable holiday-bot
        sudo systemctl start holiday-bot

        echo "✅ Сервис установлен и запущен!"
        echo "📋 Команды управления:"
        echo "   sudo systemctl status holiday-bot   - статус"
        echo "   sudo systemctl restart holiday-bot  - перезапуск"
        echo "   sudo systemctl stop holiday-bot     - остановка"
        echo "   sudo journalctl -u holiday-bot -f   - логи в реальном времени"
        ;;
    4)
        echo "👋 Выход"
        exit 0
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

echo ""
echo "🎉 Готово!"
