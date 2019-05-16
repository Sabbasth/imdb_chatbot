PNAME=imdb_chatbot
FUNC=chatbot

VENV_NAME=${PNAME}
VENV_ROOT=${HOME}/.virtualenvs
VENV=${VENV_ROOT}/${VENV_NAME}
VENV_BIN=${VENV}/bin

help:
	@echo "Makefile help"
	@echo ""
	@echo "devrun: launch a local webserver"
	@echo "deploy: Deploy the function on GCP"
	@echo "describe: Get informations on the uploaded function"
	@echo "env: Create environment for the webhook to run"
	@echo "lint: Lint the code"
	@echo "test: Macro for lint and unittest targets"
	@echo "testenv: Create development environment"
	@echo "unittest: Launch pytest tests"
	@echo ""

devrun:
	@FLASK_APP=main_emulate.py FLASK_ENV=development ${VENV_BIN}/flask run

deploy: test
	@echo "=================="
	@echo "Running deployment"
	@gcloud functions deploy ${FUNC} --runtime python37 --trigger-http --source imdb_chatbot --set-env-vars "IMDB_API_KEY=${IMDB_API_KEY}" 
	@echo "=================="

describe:
	gcloud functions describe ${FUNC}

env:
	virtualenv ${VENV}
	@${VENV_BIN}/pip3 install -r requirements.txt

lint:
	@echo Running Flake8 test
	@${VENV_BIN}/flake8 --max-line-length=99 && echo "Your style is correct!"
	@echo ===================

test: lint unittest

testenv: env
	@${VENV_BIN}/pip3 install -r test_requirements.txt

unittest:
	@echo Running py.test
	@${VENV_BIN}/python3 -m pytest
