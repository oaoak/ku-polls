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

## 3. Create `.env` file using the given `sample.env` file.

- change 'cp' to 'copy' for windows   
```
cp sample.env .env
```
- Then, follow the instructions in the `.env` file for setting up externalized variables.

## 4. Run migration

- Run the migration.

```
python manage.py migrate
```

## 5. Run tests

- Checking tests.

```
python manage.py test
```

## 6. Install data from the data fixtures

```
python manage.py loaddata data/questions-choices.json data/votes.json data/users.json
```
