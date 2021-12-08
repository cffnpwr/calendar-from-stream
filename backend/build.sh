#!/bin/sh
rm -rf */migrations
python manage.py makemigrations oauth
python manage.py migrate