## Documentation on BallDraft Backend API

### Steps to take
- create a virtual environment `python -m venv venv`
- activate virtual environment `source venv/bin/activate` (command is for macos)
- make neccessary migrations `python manage.py makemigrations`, `python manage.py migrate`
- run the api `python manage.py runserver`
- visit api docs using `localhost:8000/api/v1/auth/docs/` to consume