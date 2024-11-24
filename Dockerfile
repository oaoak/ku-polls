# Use Python as the base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy only requirements.txt first for caching
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional psycopg2 for postgres-django connection
RUN pip install psycopg2-binary

# Copy the rest of the project files
COPY . /app

# Expose the port on which the app runs
EXPOSE 8000

# Run migrations and load data
CMD ["sh", "-c", "python manage.py migrate && for file in data/*.json; do python manage.py loaddata $file; done && python manage.py runserver 0.0.0.0:8000"]

