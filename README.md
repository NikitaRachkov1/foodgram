Foodgram
========
Foodgram — это веб-приложение для публикации рецептов, добавления их в избранное и формирования списка покупок.

Стек технологий
---------------
- asgiref==3.9.1
- attrs==25.3.0
- certifi==2025.7.14
- cffi==1.17.1
- charset-normalizer==3.4.2
- cryptography==45.0.5
- defusedxml==0.7.1
- Django==4.2
- django-filter==25.1
- djangorestframework==3.16.0
- djangorestframework_simplejwt==5.5.1
- djoser==2.3.3
- drf-spectacular==0.28.0
- idna==3.10
- inflection==0.5.1
- jsonschema==4.25.0
- jsonschema-specifications==2025.4.1
- oauthlib==3.3.1
- pillow==11.3.0
- psycopg2-binary==2.9.10
- pycparser==2.22
- PyJWT==2.10.1
- python3-openid==3.2.0
- PyYAML==6.0.2
- referencing==0.36.2
- requests==2.32.4
- requests-oauthlib==2.0.0
- rpds-py==0.26.0
- social-auth-app-django==5.0.0
- social-auth-core==4.7.0
- sqlparse==0.5.3
- typing_extensions==4.14.1
- tzdata==2025.2
- uritemplate==4.2.0
- urllib3==2.5.0

Запуск проекта локально
-----------------------

Клонировать репозиторий:

.. code-block:: text

    git clone https://github.com/<your-username>/foodgram.git
    cd foodgram

Создать виртуальное окружение:

.. code-block:: text

    python -m venv venv

Активировать окружение:

- **Windows**:

  .. code-block:: text

      venv\Scripts\activate

- **Linux / macOS**:

  .. code-block:: text

      source venv/bin/activate

Установить зависимости:

.. code-block:: text

    pip install --upgrade pip
    pip install -r requirements.txt

Применить миграции:

.. code-block:: text

    python manage.py migrate

Запустить проект:

.. code-block:: text

    python manage.py runserver

Дополнительно
-------------

Создать суперпользователя:

.. code-block:: text

    python manage.py createsuperuser

Сбор статических файлов:

.. code-block:: text

    python manage.py collectstatic

Запуск проекта в Docker
------------------------

Запустить контейнеры:

.. code-block:: text

    docker-compose up -d --build

Применить миграции:

.. code-block:: text

    docker-compose exec backend python manage.py migrate

Создать суперпользователя:

.. code-block:: text

    docker-compose exec backend python manage.py createsuperuser

Собрать статику:

.. code-block:: text

    docker-compose exec backend python manage.py collectstatic --noinput

Доступ к проекту
----------------

После запуска проект будет доступен по адресу:

.. code-block:: text

    http://localhost/

Онлайн-версия проекта доступна по адресу:

.. code-block:: text

    http://89.169.161.170:8080/

Документация API:

.. code-block:: text

    http://localhost/api/docs/

Автор
-----

Разработчик: **Никита Рачков**
