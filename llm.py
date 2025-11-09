"""
Модуль для работы с LLM (OpenAI API)
"""
import openai
from config import OPENAI_API_KEY, OPENAI_MODEL, SYSTEM_PROMPT


# Настройка OpenAI клиента
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def generate_holiday_tradition(country: str, holiday_type: str) -> str:
    """
    Генерирует описание праздничных традиций для указанной страны.

    Args:
        country: Название страны
        holiday_type: Тип праздника ("Рождество" или "Новый год")

    Returns:
        Форматированный текст с описанием традиций
    """
    user_prompt = f"""Создай праздничную карточку по следующей стране и празднику:

Страна: {country}
Праздник: {holiday_type}

Формат вывода и стиль описаны в системной инструкции."""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1000,
            temperature=0.8,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Ошибка при генерации: {str(e)}"


def test_llm_connection() -> bool:
    """
    Проверяет подключение к OpenAI API.

    Returns:
        True если подключение успешно, False в противном случае
    """
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": "Привет!"}],
            max_tokens=10
        )
        return True
    except Exception as e:
        print(f"Ошибка подключения к OpenAI: {e}")
        return False


if __name__ == "__main__":
    # Тестирование модуля
    print("Тестирование подключения к OpenAI...")
    if test_llm_connection():
        print("✅ Подключение успешно!")
        print("\nГенерация примера традиции:")
        print("-" * 50)
        result = generate_holiday_tradition("Финляндия", "Рождество")
        print(result)
    else:
        print("❌ Ошибка подключения!")
