#!/bin/sh
rm -rf */migrations
python manage.py makemigrations oauth
python manage.py makemigrations user
python manage.py migrate