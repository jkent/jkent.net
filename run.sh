#!/bin/bash
export PIPENV_VENV_IN_PROJECT=1
if [[ ! -d ".venv" ]]; then
  pipenv install
fi

if [[ "$1" == "development" ]]; then
  echo "Starting in development mode"
  export FLASK_ENV=development
  rm -rf instance/cache instance/jkent_net.db instance/repository
  mkdir -p instance  
  pipenv run flask init-demo
else
  echo "Starting in production mode"
  export FLASK_ENV=production
fi 

exec pipenv run bin/gunicorn-run
