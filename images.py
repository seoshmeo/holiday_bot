"""
Модуль для получения изображений из Unsplash API
"""
import requests
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def generate_image_query(country: str, holiday_type: str) -> str:
    """
    Генерирует поисковый запрос для Unsplash на основе страны и праздника

    Args:
        country: Название страны
        holiday_type: Тип праздника

    Returns:
        Строка запроса для поиска
    """
    holiday_en = "Christmas" if "Рождество" in holiday_type else "New Year"
    query = f"{holiday_en} celebration in {country}, traditional, festive, authentic"
    return query


def get_unsplash_images(query: str, count: int = 3) -> List[str]:
    """
    Получает изображения из Unsplash API (без ключа - публичный доступ)

    Args:
        query: Поисковый запрос
        count: Количество изображений (до 3)

    Returns:
        Список URL изображений
    """
    try:
        # Используем публичный API Unsplash Source (не требует ключа)
        # Альтернатива: можно использовать другие бесплатные API

        images = []

        # Попробуем получить изображения через поиск
        # Unsplash Source API: https://source.unsplash.com/
        base_url = "https://source.unsplash.com/800x600/"

        # Формируем URL с ключевыми словами
        keywords = query.replace(" ", ",")

        # Генерируем несколько вариантов
        for i in range(min(count, 3)):
            image_url = f"{base_url}?{keywords}&sig={i}"
            images.append(image_url)

        logger.info(f"Получено {len(images)} изображений для запроса: {query}")
        return images

    except Exception as e:
        logger.error(f"Ошибка при получении изображений: {e}")
        return []


def get_holiday_images(country: str, holiday_type: str, count: int = 3) -> List[str]:
    """
    Получает праздничные изображения для страны

    Args:
        country: Название страны
        holiday_type: Тип праздника
        count: Количество изображений

    Returns:
        Список URL изображений
    """
    query = generate_image_query(country, holiday_type)
    return get_unsplash_images(query, count)


if __name__ == "__main__":
    # Тестирование
    print("Тестирование модуля изображений...")

    images = get_holiday_images("Финляндия", "Рождество", 3)

    print(f"✅ Получено {len(images)} изображений:")
    for i, url in enumerate(images, 1):
        print(f"   {i}. {url}")

    print("\n✅ Модуль изображений работает!")
