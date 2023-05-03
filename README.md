[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org) [![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org) [![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)](https://nginx.org) [![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com) [![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)](https://www.django-rest-framework.org) [![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)](https://github.com) [![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)

# Яндекс.Практикум. Спринт 17

# Описание

«Продуктовый помощник».

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Посмотреть документацию можно по адресу: http://127.0.0.1/api/docs/redoc.html

# Запуск проекта 
Склонировать репозиторий на локальную машину:
```s
git clone git@github.com:renantokbr/foodgram-project-react.git
```
Создать виртуальное окружение и обновить pip
```s
python -m venv venv
source venv/Scripts/activate
pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:

```s
pip install -r backend/requirements.txt
```

# Запуск проекта локально в контейнере:



Выполните миграции:
```
docker-compose exec backend python manage.py migrate
```
Создайте суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```
Подгрузите статику:
```
docker-compose exec backend python manage.py collectstatic --noinput
```
Загрузите список ингредиентов в базу данных:
```
docker-compose exec backend python manage.py ingredient
```
Загрузите список тегов в базу данных:
```
docker-compose exec backend python manage.py tags
```
# Выполнил студент 48 когорты Брылев Руслан 