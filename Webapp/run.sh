#!/usr/bin/env bash

# Waiting for DB
sleep 30

python ./manage.py migrate
python ./manage.py runserver 0:8000