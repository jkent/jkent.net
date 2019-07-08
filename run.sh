#!/bin/sh
export PIPENV_VENV_IN_PROJECT=1
export FLASK_ENV=development
if [ ! -f instance/jkent_net.db ]; then
  pipenv run flask init-db
  pipenv run flask add-user --password password --is-admin jeff@jkent.net
fi
exec pipenv run bin/gunicorn-run
