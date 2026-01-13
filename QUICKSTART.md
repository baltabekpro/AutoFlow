# Quick Start Guide - AutoFlow Backend

## Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка окружения
```bash
cp .env.example .env
# Отредактируйте .env и измените SECRET_KEY на что-то секретное
```

### 3. Инициализация базы данных
```bash
python init_db.py
```

### 4. Запуск сервера
```bash
uvicorn app.main:app --reload
```

Сервер будет доступен по адресу: http://localhost:8000

### 5. Открыть документацию API
Откройте в браузере: http://localhost:8000/docs

## Учетные данные по умолчанию

- **Администратор**: login=`admin`, password=`admin123`
- **Механик**: login=`mechanic1`, password=`mechanic123`

## Пример использования API

### 1. Получить токен
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 2. Получить список клиентов
```bash
curl -X GET "http://localhost:8000/clients/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Создать заказ
```bash
curl -X POST "http://localhost:8000/orders/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id": 1, "mechanic_id": 2, "mileage": 50000}'
```

### 4. Добавить товар в заказ
```bash
curl -X POST "http://localhost:8000/orders/1/add-item" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"inventory_id": 1, "description": "Моторное масло", "quantity": 2}'
```

### 5. Закрыть заказ (автоматически спишет товары со склада)
```bash
curl -X PATCH "http://localhost:8000/orders/1/status" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"status": "closed"}'
```

## Возможности системы

✅ JWT аутентификация
✅ Управление клиентами и автомобилями
✅ Создание и управление заказами
✅ Учет складских запасов
✅ Автоматический расчет стоимости заказов
✅ Автоматическое списание со склада при закрытии заказа
✅ Проверка наличия товара перед добавлением в заказ
✅ Роли пользователей (admin, mechanic)
✅ Поиск клиентов и товаров
✅ Фильтрация заказов по статусу
✅ Полная документация API (Swagger/OpenAPI)
