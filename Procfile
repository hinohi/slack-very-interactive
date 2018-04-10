web: gunicorn very.very.web:web --log-file=-
worker: celery worker --config=very.very.conf --loglevel=info
worker: python3 run/slackbot.py
