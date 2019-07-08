#!/bin/sh
export PIPENV_VENV_IN_PROJECT=1
export FLASK_ENV=development
if [ ! -d .venv ]; then
  pipenv install
fi
mkdir -p instance
rm -r instance/jkent_net.db
pipenv run flask init-db
pipenv run flask add-user --password password --is-admin jeff@jkent.net
exec pipenv run bin/gunicorn-run
