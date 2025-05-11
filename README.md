# Foodgram — Платформа для публикации и обмена рецептами

## О проекте

**Foodgram** — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Платформа позволяет:
- Публиковать собственные рецепты
- Добавлять рецепты в избранное
- Формировать и скачивать списки покупок
- Подписываться на других авторов
- Искать ингредиенты и рецепты по фильтрам

## Проект состоит из следующих страниц:
- Главная,
- Страница входа,
- Страница регистрации,
- Страница рецепта,
- Страница пользователя,
- Страница подписок,
- Избранное,
- Список покупок,
- Создание и редактирование рецепта,
- Страница смены пароля,
- Статические страницы «О проекте» и «Технологии».

## Технологии

- Python 3.10+
- Django, Django REST Framework
- PostgreSQL
- Docker, Docker Compose
- Nginx
- Djoser (аутентификация)
- Pillow (работа с изображениями)

## Быстрый старт

### 1. Клонирование репозитория

```sh
git clone https://github.com/MaximFLUNN/foodgram-st.git
cd foodgram-st
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
DJANGO_SECRET_KEY='v&%qj3_!a(s*m^2@p9$c+b1!z@_w#x&y8k(f@g!h'
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1,backend,your_domain.com'

POSTGRES_DB=foodgram_db
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD='pass'

DATABASE_URL=postgresql://foodgram_user:pass@db:5432/foodgram_db
```

### 3. Сборка и запуск контейнеров

```sh
docker-compose up -d --build
```

### 4. Первоначальная настройка проекта

Выполните миграции, загрузите ингредиенты, соберите статику и создайте суперпользователя:

```sh
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py load_ingredients
docker-compose exec backend python manage.py collectstatic --noinput
docker-compose exec backend python manage.py createsuperuser
```

### 5. Доступ к проекту

- **Главная страница:** [http://localhost/](http://localhost/)
- **API-документация:** [http://localhost/api/docs/](http://localhost/api/docs/)
- **Админ-панель:** [http://localhost/admin/](http://localhost/admin/)

### 6. Тестирование API

- Примеры запросов и тесты доступны в коллекции Postman:
  `postman_collection/foodgram.postman_collection.json`

## Особенности реализации

- Кастомная модель пользователя с email в качестве логина
- Поддержка пагинации с параметром `limit`
- Фильтрация ингредиентов по первым буквам
- Короткие ссылки на рецепты (`/s/<id>/`)
- Корзина покупок и избранное реализованы через отдельные модели
- Возможность скачивания списка покупок в формате `.txt`

## Контакты

Автор: [Максим](https://github.com/MaximFLUNN)

---
