#!/usr/bin/env bash

rm .env
heroku config:get AUTH -s >> .env
heroku config:get DATABASE_URL -s >> .env
heroku config:get SALT -s >> .env
heroku config:get DB_HOST -s >> .env
heroku config:get DB_DATABASE -s >> .env
heroku config:get DB_USER -s >> .env
heroku config:get DB_PASSWORD -s >> .env
heroku config:get MEMCACHEDCLOUD_PASSWORD -s >> .env
heroku config:get MEMCACHEDCLOUD_SERVERS -s >> .env
heroku config:get MEMCACHEDCLOUD_USERNAME -s >> .env
heroku config:get REDIS_URL -s >> .env
heroku config:get TBA_KEY -s >> .env
echo "PYTHONUNBUFFERED=1" >> .env
echo "FLASK_ENV=development" >> .env
