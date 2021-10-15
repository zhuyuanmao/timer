#!/bin/sh

python manage.py flush --no-input
python mange.oy makemigrations pomodoro
python manage.py migrate
#python manage.py collectstatic --no-input --clear

exec "$@"