#!/bin/bash
export PIPENV_VENV_IN_PROJECT=1
if [[ ! -d ".venv" ]]; then
  pipenv install
fi

args="-b 0.0.0.0:18080 -k gevent"

if [[ "$1" =~ ^dev.* ]]; then
  echo "Starting in development mode"
  export FLASK_ENV=development
  rm -rf instance/cache instance/jkent_net.db
  mkdir -p instance  
  pipenv run flask init-db
  pipenv run flask create-role admin Administrator
  pipenv run flask create-user user@example.com --password password
  pipenv run flask create-user admin@example.com --password password --is-admin
  pipenv run flask create-user jeff@jkent.net --is-admin
  args="$args --reload"
else
  echo "Starting in production mode"
  export FLASK_ENV=production
fi 

exec pipenv run gunicorn $args wsgi:app
