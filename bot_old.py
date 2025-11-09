"""
Telegram бот для генерации праздничных традиций разных стран
"""
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from config import TELEGRAM_BOT_TOKEN
from countries import COUNTRIES, HOLIDAY_TYPES
from llm import generate_holiday_tradition

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    welcome_message = """
Привет! Я Holiday Traditions Bot!

Я помогу тебе узнать, как празднуют Рождество и Новый год в разных странах мира.

Доступные команды:
/holiday - Случайная страна и праздник
/christmas - Традиции Рождества в случайной стране
/newyear - Традиции Нового года в случайной стране
/another - Повторить с другой страной

Каждая подборка включает:
- Традиционные наряды
- Обычаи и блюда
- Подходящий фильм
- Песню или музыку
- Совет, как адаптировать традицию дома

Попробуй /holiday прямо сейчас!
"""
    await update.message.reply_text(welcome_message)


async def holiday_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /holiday - случайная страна и случайный тип праздника"""
    country = random.choice(COUNTRIES)
    holiday_type = random.choice(list(HOLIDAY_TYPES.values()))

    # Сохраняем выбранные параметры для команды /another
    context.user_data['last_country'] = country
    context.user_data['last_holiday'] = holiday_type

    await send_holiday_info(update, country, holiday_type)


async def christmas_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /christmas - Рождество в случайной стране"""
    country = random.choice(COUNTRIES)
    holiday_type = HOLIDAY_TYPES['christmas']

    context.user_data['last_country'] = country
    context.user_data['last_holiday'] = holiday_type

    await send_holiday_info(update, country, holiday_type)


async def newyear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /newyear - Новый год в случайной стране"""
    country = random.choice(COUNTRIES)
    holiday_type = HOLIDAY_TYPES['newyear']

    context.user_data['last_country'] = country
    context.user_data['last_holiday'] = holiday_type

    await send_holiday_info(update, country, holiday_type)


async def another_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /another - повторить с другой страной"""
    # Используем последний тип праздника, если он был сохранен
    last_holiday = context.user_data.get('last_holiday')

    if not last_holiday:
        # Если нет сохраненного типа, выбираем случайный
        last_holiday = random.choice(list(HOLIDAY_TYPES.values()))

    # Выбираем новую страну
    country = random.choice(COUNTRIES)

    context.user_data['last_country'] = country
    context.user_data['last_holiday'] = last_holiday

    await send_holiday_info(update, country, last_holiday)


async def send_holiday_info(update: Update, country: str, holiday_type: str) -> None:
    """
    Генерирует и отправляет информацию о празднике

    Args:
        update: Telegram Update объект
        country: Название страны
        holiday_type: Тип праздника
    """
    # Отправляем сообщение о начале генерации
    status_message = await update.message.reply_text(
        f"Генерирую информацию о праздновании в стране {country}..."
    )

    # Генерируем традиции через LLM
    result = generate_holiday_tradition(country, holiday_type)

    # Удаляем статусное сообщение
    await status_message.delete()

    # Создаем inline-кнопки
    keyboard = [
        [
            InlineKeyboardButton("Другая страна", callback_data="another"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем результат
    await update.message.reply_text(
        result,
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на inline-кнопки"""
    query = update.callback_query
    await query.answer()

    if query.data == "another":
        # Получаем последний тип праздника
        last_holiday = context.user_data.get('last_holiday')

        if not last_holiday:
            last_holiday = random.choice(list(HOLIDAY_TYPES.values()))

        # Выбираем новую страну
        country = random.choice(COUNTRIES)

        context.user_data['last_country'] = country
        context.user_data['last_holiday'] = last_holiday

        # Отправляем сообщение о генерации
        status_message = await query.message.reply_text(
            f"Генерирую информацию о праздновании в стране {country}..."
        )

        # Генерируем традиции
        result = generate_holiday_tradition(country, last_holiday)

        # Удаляем статусное сообщение
        await status_message.delete()

        # Создаем кнопки
        keyboard = [
            [
                InlineKeyboardButton("Другая страна", callback_data="another"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем результат
        await query.message.reply_text(
            result,
            reply_markup=reply_markup
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")

    if update and update.message:
        await update.message.reply_text(
            "Произошла ошибка при обработке запроса. Попробуйте еще раз."
        )


def main() -> None:
    """Основная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("holiday", holiday_command))
    application.add_handler(CommandHandler("christmas", christmas_command))
    application.add_handler(CommandHandler("newyear", newyear_command))
    application.add_handler(CommandHandler("another", another_command))

    # Регистрируем обработчик callback-кнопок
    application.add_handler(CallbackQueryHandler(button_callback))

    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    logger.info("Бот запускается...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
