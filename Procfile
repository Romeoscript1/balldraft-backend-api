web: python manage.py migrate && gunicorn balldraft.wsgi:application --workers 3 --bind 0.0.0.0:8000 --log-file -
worker: celery -A blog worker -l info
beat: celery -A i blog beat -l info
