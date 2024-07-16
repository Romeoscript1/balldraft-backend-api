web: python manage.py migrate && gunicorn balldraft.wsgi:application --workers 3 --bind 0.0.0.0:9000 --log-file -
worker: celery -A balldraft worker -l info
beat: celery -A balldraft beat -l info
