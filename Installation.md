# Installation steps

## 1. Cloning

- Clone this repository to your local machine.

```
git clone https://github.com/oaoak/ku-polls.git your_directory_name
```
**NOTED**: ***your_directory_name*** in the field is ***your*** desired directory name.

- Change your directory if you are not on it.

```
cd your_directory_name
```

## 2. Create virtual environment and install packages

- Create virtual environment.

```
python -m venv env
```

- Change to your newly created virtual environment.

```
. env/bin/activate
```

- Install packages from requirements.txt

```
pip install -r requirements.txt
```

## 3. Run migration

- Run the migration.

```
python manage.py migrate
```

## 4. Run tests

- Checking tests.

```
python manage.py test
```

## 5. Install data from the data fixtures

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
