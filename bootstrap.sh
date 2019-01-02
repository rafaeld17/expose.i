#!/bin/sh
export FLASK_APP=./imageAnalysis/index.py
source $(pipenv --venv)/bin/activate
flask run -h localhost
