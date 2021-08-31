#!/usr/bin/env bash

# docker-compose handles waiting for DB via depends_on condition

python ./manage.py migrate
gunicorn Webapp.wsgi -b :8000
# python ./manage.py runserver 0:8000
