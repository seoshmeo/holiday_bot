# Настройка Unsplash API для изображений

## Зачем нужен Unsplash API?

Бот автоматически добавляет до 3 праздничных фотографий к каждому ответу. Для этого используется бесплатный Unsplash API.

---

## Получение API ключа (бесплатно)

### Шаг 1: Регистрация

1. Перейдите на https://unsplash.com/developers
2. Нажмите **"Register as a developer"**
3. Войдите через существующий аккаунт или создайте новый

### Шаг 2: Создание приложения

1. После входа нажмите **"New Application"**
2. Примите условия использования API
3. Заполните форму:
   - **Application name**: `Holiday Traditions Bot`
   - **Description**: `Telegram bot that shows holiday traditions from different countries`
4. Нажмите **"Create application"**

### Шаг 3: Получение Access Key

1. После создания приложения вы увидите страницу с деталями
2. Найдите раздел **"Keys"**
3. Скопируйте **"Access Key"** (длинная строка из букв и цифр)

---

## Добавление ключа в бот

### Локально (на вашем компьютере):

Откройте файл `.env` и добавьте строку:

```env
UNSPLASH_ACCESS_KEY=ваш_access_key_здесь
```

Пример:
```env
TELEGRAM_BOT_TOKEN=7784405747:AAEUDA60YNrtWaeOMGL2koNqSyADySClvzE
OPENAI_API_KEY=sk-proj-8cCtkpaA...
OPENAI_MODEL=gpt-4o-mini
UNSPLASH_ACCESS_KEY=abcd1234efgh5678ijkl9012mnop3456qrst7890
```

### На сервере:

```bash
cd ~/bots/holiday_bot
nano .env
```

Добавьте строку:
```env
UNSPLASH_ACCESS_KEY=ваш_access_key_здесь
```

Сохраните: `Ctrl+X` → `Y` → `Enter`

Перезапустите бота:
```bash
sudo systemctl restart holiday-traditions-bot
```

---

## Проверка работы

### Тест модуля:

```bash
cd ~/bots/holiday_bot
source venv/bin/activate
python images.py
```

Должно вывести:
```
✅ Получено 3 изображений:
   1. https://images.unsplash.com/photo-...
   2. https://images.unsplash.com/photo-...
   3. https://images.unsplash.com/photo-...

✅ Модуль изображений работает!
```

### Тест в боте:

Отправьте боту `/holiday` - должны прийти фотографии вместе с текстом.

---

## Лимиты бесплатного плана

Unsplash бесплатно предоставляет:
- ✅ **50 запросов в час**
- ✅ Неограниченное количество приложений
- ✅ Доступ к миллионам бесплатных фотографий

Этого достаточно для ~15-20 пользователей в час.

---

## Что если нет API ключа?

Бот работает и без Unsplash API - просто не будет отправлять изображения. Все остальные функции работают нормально.

---

## Устранение проблем

### Ошибка 401 (Unauthorized)

- Проверьте правильность API ключа
- Убедитесь, что нет лишних пробелов
- Проверьте, что приложение активно на Unsplash

### Ошибка 403 (Forbidden / Rate Limit)

- Превышен лимит 50 запросов/час
- Подождите час или создайте новое приложение

### Нет изображений по запросу

- Это нормально для некоторых стран
- Бот автоматически отправит только текст

### Изображения не отправляются

Проверьте логи:
```bash
sudo journalctl -u holiday-traditions-bot -n 50 | grep -i image
```

---

## Альтернативы Unsplash

Если не хотите использовать Unsplash, можно:

1. **Оставить без изображений** - бот работает без них
2. **Использовать Pexels API** - похожий бесплатный сервис
3. **Генерировать через DALL-E** - потребует дополнительных токенов OpenAI

---

## Итого: Быстрая настройка

```bash
# 1. Получите ключ на unsplash.com/developers
# 2. Откройте .env
nano .env

# 3. Добавьте строку
UNSPLASH_ACCESS_KEY=ваш_ключ

# 4. Перезапустите бота
sudo systemctl restart holiday-traditions-bot

# 5. Проверьте
python images.py
```

**Готово! Теперь бот отправляет красивые фотографии.**
