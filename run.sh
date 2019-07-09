#!/bin/bash
export PIPENV_VENV_IN_PROJECT=1
if [[ ! -d ".venv" ]]; then
  pipenv install
fi

if [[ "$1" == "development" ]]; then
  echo "Starting in development mode"
  export FLASK_ENV=development
  mkdir -p instance
  rm -f instance/jkent_net.db
  pipenv run flask init-db
  pipenv run flask add-user --password password --is-admin jeff@jkent.net
else
  echo "Starting in production mode"
  export FLASK_ENV=production
fi 

exec pipenv run bin/gunicorn-run