#!/bin/sh
export PIPENV_VENV_IN_PROJECT=1
export FLASK_ENV=production
if [ ! -d .venv ]; then
  pipenv install
fi
exec pipenv run bin/gunicorn-run
