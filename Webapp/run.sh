#!/usr/bin/env bash

# docker-compose handles waiting for DB via depends_on condition

python ./manage.py migrate
python ./manage.py runserver 0:8000