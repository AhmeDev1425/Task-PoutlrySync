#!/bin/sh

echo "Waiting for MySQL to be ready..."
until mysqladmin ping -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" --silent; do
  echo "MySQL is unavailable - sleeping"
  sleep 2
done


echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Seeding initial data..."
python manage.py seed_data


echo "Starting Gunicorn..."
exec gunicorn project.wsgi:application --bind 0.0.0.0:8000
