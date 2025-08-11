#!/bin/sh
set -e 
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:=foodgram.settings}"
export GUNICORN_APP="${GUNICORN_APP:=foodgram.wsgi:application}"

exec gunicorn "$GUNICORN_APP" --bind 0.0.0.0:8000
