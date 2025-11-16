#!/bin/sh

echo "Waiting for MySQL to be ready..."
for i in {1..30}; do
  if mysqladmin ping -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" --silent; then
    echo "MySQL is up!"
    break
  fi
  echo "MySQL is unavailable - sleeping"
  sleep 5
done


echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Seeding initial data..."
python manage.py seed_data


echo "Starting Gunicorn..."
exec gunicorn project.wsgi:application --bind 0.0.0.0:8000
