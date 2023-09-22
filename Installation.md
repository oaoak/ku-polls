# Installation steps

## 1. Create virtual environment and install packages

- Create virtual environment.

```
python -m venv env
```

- Install packages from requirements.txt

```
pip install -r requirements.txt
```

## 2. Run migration

- Run the migration.

```
python manage.py migrate
```

## 3. Run tests

- Checking tests.

```
python manage.py test
```

## 4. Install data from the data fixtures

- Load questions data.

```
python manage.py loaddata data/questions.json
```

- Load choices data.

```
python manage.py loaddata data/choices.json
```

- Load users data.

```
python manage.py loaddata data/users.json
```
