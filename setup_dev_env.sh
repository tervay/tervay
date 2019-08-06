#!/usr/bin/env bash

heroku config:get AUTH -s >> .env
heroku config:get DATABASE_URL -s >> .env
heroku config:get SALT -s >> .env
heroku config:get DB_HOST -s >> .env
heroku config:get DB_DATABASE -s >> .env
heroku config:get DB_USER -s >> .env
heroku config:get DB_PASSWORD -s >> .env
echo "PYTHONUNBUFFERED=1" >> .env
echo "FLASK_ENV=development" >> .env
