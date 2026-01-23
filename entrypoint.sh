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
    # --timeout 600: Render無料枠の「Cold Start (スリープからの復帰)」対策。起動に時間がかかっても殺されないように10分待つ。
    # --workers 2: 処理を並列化して、片方が詰まってももう片方が応答できるようにする（お守り）。
    # --log-level debug: エラー原因を特定するために詳細なログを出す。
    exec gunicorn circle_app.wsgi:application --bind 0.0.0.0:$PORT --timeout 600 --workers 2 --log-level debug
else
    exec "$@"
fi
