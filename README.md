# Jouer Flux

This API simulate an API capable of managing Firewalls.

## Install

### Initialize virtual environment (Optional)

#### Create a virtual environment

```
python -m venv venv
```

#### Activate the virtual environment

```
source venv/bin/activate
```

### Install the dependencies

```
pip install -r requirements.txt
```

### Initialize database

```
alembic upgrade head
```

### Run the `manage.py` file

```
python manage.py
```

### Enjoy

The API is now running and also usable through [swagger](http://localhost:8000/ui/).

## Note

This API was made in a short time and lacks a lot of features:
- Documentation
- Authentication
- Pagination
- Better Error Handling
- Logs
- Tests
- Configuration through env files
- ...

This API's endpoints are idempotents (They give the same results regardless of how much time they are called).