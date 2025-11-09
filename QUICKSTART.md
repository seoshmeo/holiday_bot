# Быстрый старт

## Шаг 1: Установка зависимостей

```bash
cd holiday_bot
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Шаг 2: Создание .env файла

```bash
cp .env.example .env
```

Откройте `.env` и заполните:

```env
TELEGRAM_BOT_TOKEN=получите_у_@BotFather
OPENAI_API_KEY=получите_на_platform.openai.com
OPENAI_MODEL=gpt-4o-mini
```

## Шаг 3: Тестирование

```bash
python llm.py
```

Должно вывести пример генерации традиций.

## Шаг 4: Запуск бота

```bash
python bot.py
```

## Шаг 5: Тестирование в Telegram

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Отправьте `/holiday`
4. Наслаждайтесь!

## Получение токенов

### Telegram Bot Token

1. Откройте [@BotFather](https://t.me/botfather)
2. Команда: `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен

### OpenAI API Key

1. Перейдите на [platform.openai.com](https://platform.openai.com)
2. Зарегистрируйтесь/войдите
3. Перейдите в API Keys
4. Создайте новый ключ
5. Скопируйте ключ (он больше не будет показан!)

## Проверка

Команда для проверки токена Telegram:

```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

Должен вернуть JSON с информацией о боте.

## Частые ошибки

**Ошибка**: ModuleNotFoundError
**Решение**: Убедитесь, что активировали виртуальное окружение

**Ошибка**: Токен не найден
**Решение**: Проверьте, что `.env` файл создан и заполнен

**Ошибка**: OpenAI API error
**Решение**: Проверьте баланс на platform.openai.com

## Минимальные требования

- Python 3.8+
- Активный токен Telegram бота
- OpenAI API ключ с положительным балансом
- Доступ к интернету
