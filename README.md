Foodgram
========
Foodgram — это веб-приложение для публикации рецептов, добавления их в избранное и формирования списка покупок.

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

Документация API:

.. code-block:: text

    http://localhost/api/docs/
