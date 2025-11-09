"""
Модуль для получения изображений из Unsplash API
"""
import requests
from typing import List, Optional
import logging
from config import UNSPLASH_ACCESS_KEY

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
    query = f"{holiday_en} {country} celebration traditional"
    return query


def get_unsplash_images(query: str, count: int = 3) -> List[str]:
    """
    Получает изображения из Unsplash API

    Args:
        query: Поисковый запрос
        count: Количество изображений (до 3)

    Returns:
        Список URL изображений
    """
    # Если нет ключа API, возвращаем пустой список
    if not UNSPLASH_ACCESS_KEY:
        logger.warning("UNSPLASH_ACCESS_KEY не установлен, изображения не будут загружены")
        return []

    try:
        # Официальный Unsplash API
        url = "https://api.unsplash.com/search/photos"

        headers = {
            "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
        }

        params = {
            "query": query,
            "per_page": min(count, 3),
            "orientation": "landscape"
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            images = []

            for photo in data.get("results", [])[:count]:
                # Используем regular размер для баланса качества и скорости
                image_url = photo.get("urls", {}).get("regular")
                if image_url:
                    images.append(image_url)

            logger.info(f"Получено {len(images)} изображений для запроса: {query}")
            return images

        elif response.status_code == 401:
            logger.error("Неверный Unsplash API ключ")
            return []

        elif response.status_code == 403:
            logger.error("Превышен лимит запросов Unsplash API")
            return []

        else:
            logger.warning(f"Unsplash API вернул статус {response.status_code}")
            return []

    except requests.exceptions.Timeout:
        logger.error("Timeout при запросе к Unsplash API")
        return []

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

    if not UNSPLASH_ACCESS_KEY:
        print("⚠️  UNSPLASH_ACCESS_KEY не установлен в .env файле")
        print("📝 Получите ключ на https://unsplash.com/developers")
        print("   1. Зарегистрируйтесь")
        print("   2. Создайте приложение")
        print("   3. Скопируйте Access Key")
        print("   4. Добавьте в .env файл: UNSPLASH_ACCESS_KEY=ваш_ключ")
    else:
        images = get_holiday_images("Финляндия", "Рождество", 3)

        if images:
            print(f"✅ Получено {len(images)} изображений:")
            for i, url in enumerate(images, 1):
                print(f"   {i}. {url[:80]}...")
            print("\n✅ Модуль изображений работает!")
        else:
            print("❌ Изображения не получены. Проверьте API ключ и лимиты.")
