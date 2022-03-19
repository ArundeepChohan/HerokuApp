web: gunicorn portfolio.wsgi
worker: celery -A portfolio worker -l info 
beat: celery -A portfolio beat -l info 
release: python manage.py migrate