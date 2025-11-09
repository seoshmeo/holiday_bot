"""
Модуль для работы с базой данных (кэширование ответов)
"""
import sqlite3
from datetime import datetime
from typing import Optional, Tuple


class Database:
    """Класс для работы с SQLite базой данных"""

    def __init__(self, db_path: str = "holiday_bot.db"):
        """
        Инициализация базы данных

        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Создание таблиц, если их нет"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS holiday_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT NOT NULL,
                holiday_type TEXT NOT NULL,
                response_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(country, holiday_type)
            )
        """)

        conn.commit()
        conn.close()

    def get_response(self, country: str, holiday_type: str) -> Optional[str]:
        """
        Получить ответ из кэша

        Args:
            country: Название страны
            holiday_type: Тип праздника

        Returns:
            Текст ответа или None если не найден
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT response_text FROM holiday_responses WHERE country = ? AND holiday_type = ?",
            (country, holiday_type)
        )

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    def save_response(self, country: str, holiday_type: str, response_text: str):
        """
        Сохранить ответ в кэш

        Args:
            country: Название страны
            holiday_type: Тип праздника
            response_text: Текст ответа
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO holiday_responses (country, holiday_type, response_text)
            VALUES (?, ?, ?)
            """,
            (country, holiday_type, response_text)
        )

        conn.commit()
        conn.close()

    def get_stats(self) -> Tuple[int, int]:
        """
        Получить статистику базы данных

        Returns:
            Кортеж (количество стран, количество записей)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(DISTINCT country) FROM holiday_responses")
        countries_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM holiday_responses")
        total_count = cursor.fetchone()[0]

        conn.close()

        return countries_count, total_count

    def clear_cache(self):
        """Очистить весь кэш"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM holiday_responses")

        conn.commit()
        conn.close()


if __name__ == "__main__":
    # Тестирование базы данных
    db = Database()

    print("Тестирование базы данных...")

    # Сохранение
    db.save_response("Финляндия", "Рождество", "Тестовый ответ про Финляндию")
    print("✅ Ответ сохранён")

    # Получение
    response = db.get_response("Финляндия", "Рождество")
    print(f"✅ Ответ получен: {response[:50]}...")

    # Статистика
    countries, total = db.get_stats()
    print(f"✅ Статистика: {countries} стран, {total} записей")

    print("\n✅ База данных работает корректно!")
