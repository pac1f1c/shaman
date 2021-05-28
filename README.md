Shaman
==============

**Shaman** is Django database-driven Telegram bot that uses asynchronous task queue Celery to handle webhook updates in the background.


Testing
---------------------
Use ngrok to run the bot.
Use Docker to install required services:

    docker docker-compose up -d

Run ngrok:


    ngrok http 8000

Create the ``.env`` file the in current directory:

    SECRET_KEY=...
    CHATBOT_WEBHOOK_DOMAIN=https://...ngrok.io
    CHATBOT_NAME=@...
    CHATBOT_TOKEN=...

Put there a Django ``SECRET_KEY`` and the ngrok domain. Create a new telegram bot via ``@BotFather``.

Create a virtual environment, install the requirements, run Django server:

    python3 -m venv ./venv/
    source ./venv/bin/activate
    python manage.py runserver

Run celery worker in another terminal window:


    $ celery -A django_chatbot worker -l DEBUG
