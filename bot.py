"""
Telegram бот для генерации праздничных традиций разных стран
Версия 2.0 с базой данных и изображениями
"""
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from config import TELEGRAM_BOT_TOKEN
from countries import COUNTRIES, HOLIDAY_TYPES
from llm import generate_holiday_tradition
from database import Database
from images import get_holiday_images

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
db = Database()

# Состояния для ConversationHandler
CHOOSING_COUNTRY, CHOOSING_HOLIDAY = range(2)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    welcome_message = """
🎄 Привет! Я Holiday Traditions Bot!

Я помогу тебе узнать, как празднуют Рождество и Новый год в разных странах мира.

📋 Доступные команды:
/holiday - Случайная страна и праздник
/christmas - Традиции Рождества в случайной стране
/newyear - Традиции Нового года в случайной стране
/custom - Выбрать страну самостоятельно
/another - Повторить с другой страной
/stats - Статистика базы данных

✨ Каждая подборка включает:
- Традиционные наряды
- Обычаи и блюда
- Подходящий фильм
- Песню или музыку
- Совет, как адаптировать традицию дома
- Праздничные фотографии

Попробуй /holiday прямо сейчас!
"""
    await update.message.reply_text(welcome_message)


async def holiday_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /holiday - случайная страна и случайный тип праздника"""
    country = random.choice(COUNTRIES)
    holiday_type = random.choice(list(HOLIDAY_TYPES.values()))

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


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало выбора кастомной страны"""
    keyboard = [
        [InlineKeyboardButton("🎲 Случайная страна", callback_data="random_country")],
        [InlineKeyboardButton("✍️ Ввести страну", callback_data="type_country")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Как выбрать страну?",
        reply_markup=reply_markup
    )
    return CHOOSING_COUNTRY


async def another_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /another - повторить с другой страной"""
    last_holiday = context.user_data.get('last_holiday')

    if not last_holiday:
        last_holiday = random.choice(list(HOLIDAY_TYPES.values()))

    country = random.choice(COUNTRIES)

    context.user_data['last_country'] = country
    context.user_data['last_holiday'] = last_holiday

    await send_holiday_info(update, country, last_holiday)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Статистика базы данных"""
    countries_count, total_count = db.get_stats()

    stats_message = f"""
📊 Статистика базы данных:

🌍 Стран в кэше: {countries_count}
📝 Всего ответов: {total_count}
💾 База данных: SQLite

Кэшированные ответы загружаются мгновенно!
"""
    await update.message.reply_text(stats_message)


async def handle_country_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора способа указания страны"""
    query = update.callback_query
    await query.answer()

    if query.data == "random_country":
        # Случайная страна
        country = random.choice(COUNTRIES)
        context.user_data['custom_country'] = country

        # Выбор праздника
        keyboard = [
            [InlineKeyboardButton("🎄 Рождество", callback_data="custom_christmas")],
            [InlineKeyboardButton("🎆 Новый год", callback_data="custom_newyear")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Выбрана страна: {country}\n\nКакой праздник?",
            reply_markup=reply_markup
        )
        return CHOOSING_HOLIDAY

    elif query.data == "type_country":
        await query.edit_message_text(
            "Введите название страны (на русском):\n\nНапример: Япония, Франция, Бразилия"
        )
        return CHOOSING_COUNTRY


async def handle_typed_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка введённой страны"""
    country = update.message.text.strip()
    context.user_data['custom_country'] = country

    # Выбор праздника
    keyboard = [
        [InlineKeyboardButton("🎄 Рождество", callback_data="custom_christmas")],
        [InlineKeyboardButton("🎆 Новый год", callback_data="custom_newyear")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Отлично! Выбрана страна: {country}\n\nКакой праздник?",
        reply_markup=reply_markup
    )
    return CHOOSING_HOLIDAY


async def handle_holiday_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора праздника"""
    query = update.callback_query
    await query.answer()

    country = context.user_data.get('custom_country')
    holiday_type = HOLIDAY_TYPES['christmas'] if 'christmas' in query.data else HOLIDAY_TYPES['newyear']

    context.user_data['last_country'] = country
    context.user_data['last_holiday'] = holiday_type

    # Создаём фейковый update для send_holiday_info
    await query.edit_message_text(f"Генерирую информацию о праздновании в стране {country}...")

    # Получаем информацию
    response_text = await get_or_generate_response(country, holiday_type)

    # Получаем изображения
    images = get_holiday_images(country, holiday_type, count=3)

    # Удаляем статусное сообщение
    await query.message.delete()

    # Создаем кнопки
    keyboard = [
        [InlineKeyboardButton("Другая страна", callback_data="another")],
        [InlineKeyboardButton("Выбрать страну", callback_data="custom")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем с изображениями
    if images:
        # Отправляем изображения группой
        media_group = [InputMediaPhoto(media=url) for url in images[:3]]
        await query.message.reply_media_group(media=media_group)

        # Отправляем текст отдельно
        await query.message.reply_text(response_text, reply_markup=reply_markup)
    else:
        await query.message.reply_text(response_text, reply_markup=reply_markup)

    return ConversationHandler.END


async def send_holiday_info(update: Update, country: str, holiday_type: str) -> None:
    """Генерирует и отправляет информацию о празднике"""
    # Отправляем сообщение о начале генерации
    status_message = await update.message.reply_text(
        f"Генерирую информацию о праздновании в стране {country}..."
    )

    # Проверяем кэш или генерируем новый ответ
    response_text = await get_or_generate_response(country, holiday_type)

    # Получаем изображения
    logger.info(f"Получение изображений для {country}, {holiday_type}")
    images = get_holiday_images(country, holiday_type, count=3)

    # Удаляем статусное сообщение
    await status_message.delete()

    # Создаем inline-кнопки
    keyboard = [
        [InlineKeyboardButton("Другая страна", callback_data="another")],
        [InlineKeyboardButton("Выбрать страну", callback_data="custom")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем результат с изображениями
    if images:
        try:
            # Отправляем изображения группой
            media_group = [InputMediaPhoto(media=url) for url in images[:3]]
            await update.message.reply_media_group(media=media_group)

            # Отправляем текст отдельно
            await update.message.reply_text(response_text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Ошибка при отправке изображений: {e}")
            # Если не удалось отправить изображения, отправляем только текст
            await update.message.reply_text(response_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(response_text, reply_markup=reply_markup)


async def get_or_generate_response(country: str, holiday_type: str) -> str:
    """
    Получает ответ из кэша или генерирует новый

    Args:
        country: Название страны
        holiday_type: Тип праздника

    Returns:
        Текст ответа
    """
    # Проверяем кэш
    cached = db.get_response(country, holiday_type)

    if cached:
        logger.info(f"Ответ для {country} ({holiday_type}) взят из кэша")
        return f"💾 {cached}"

    # Генерируем новый ответ
    logger.info(f"Генерация нового ответа для {country} ({holiday_type})")
    response = generate_holiday_tradition(country, holiday_type)

    # Сохраняем в кэш
    db.save_response(country, holiday_type, response)
    logger.info(f"Ответ для {country} ({holiday_type}) сохранён в кэш")

    return response


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на inline-кнопки"""
    query = update.callback_query
    await query.answer()

    if query.data == "another":
        last_holiday = context.user_data.get('last_holiday')

        if not last_holiday:
            last_holiday = random.choice(list(HOLIDAY_TYPES.values()))

        country = random.choice(COUNTRIES)

        context.user_data['last_country'] = country
        context.user_data['last_holiday'] = last_holiday

        # Статусное сообщение
        status_message = await query.message.reply_text(
            f"Генерирую информацию о праздновании в стране {country}..."
        )

        # Получаем ответ
        response_text = await get_or_generate_response(country, last_holiday)

        # Получаем изображения
        images = get_holiday_images(country, last_holiday, count=3)

        # Удаляем статус
        await status_message.delete()

        # Кнопки
        keyboard = [
            [InlineKeyboardButton("Другая страна", callback_data="another")],
            [InlineKeyboardButton("Выбрать страну", callback_data="custom")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем
        if images:
            try:
                media_group = [InputMediaPhoto(media=url) for url in images[:3]]
                await query.message.reply_media_group(media=media_group)
                await query.message.reply_text(response_text, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Ошибка при отправке изображений: {e}")
                await query.message.reply_text(response_text, reply_markup=reply_markup)
        else:
            await query.message.reply_text(response_text, reply_markup=reply_markup)

    elif query.data == "custom":
        # Запускаем выбор страны
        keyboard = [
            [InlineKeyboardButton("🎲 Случайная страна", callback_data="random_country")],
            [InlineKeyboardButton("✍️ Ввести страну", callback_data="type_country")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            "Как выбрать страну?",
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

    # ConversationHandler для выбора кастомной страны
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("custom", custom_command)],
        states={
            CHOOSING_COUNTRY: [
                CallbackQueryHandler(handle_country_choice, pattern="^(random_country|type_country)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_typed_country),
            ],
            CHOOSING_HOLIDAY: [
                CallbackQueryHandler(handle_holiday_choice, pattern="^custom_(christmas|newyear)$"),
            ],
        },
        fallbacks=[CommandHandler("start", start_command)],
    )

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("holiday", holiday_command))
    application.add_handler(CommandHandler("christmas", christmas_command))
    application.add_handler(CommandHandler("newyear", newyear_command))
    application.add_handler(CommandHandler("another", another_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(conv_handler)

    # Регистрируем обработчик callback-кнопок
    application.add_handler(CallbackQueryHandler(button_callback))

    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    logger.info("Бот запускается...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
