web: gunicorn portfolio.wsgi
worker: celery -A portfolio worker -l info -B
worker: celery -A portfolio beat -l info -B
release: python manage.py migrate