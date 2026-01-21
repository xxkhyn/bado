#!/bin/sh

# if [ "$DATABASE" = "postgres" ]
# then
#     echo "Waiting for postgres..."
#
#     while ! nc -z $SQL_HOST $SQL_PORT; do
#       sleep 0.1
#     done
#
#     echo "PostgreSQL started"
# fi


python manage.py collectstatic --no-input
python manage.py migrate


if [ -z "$1" ]; then
    echo "No command provided, starting Gunicorn..."
    exec gunicorn circle_app.wsgi:application --bind 0.0.0.0:$PORT
else
    exec "$@"
fi
