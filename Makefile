.PHONY: help install run shell db-init db-migrate db-upgrade clean

VENV?=.venv
PYTHON?=python3
PIP:=$(VENV)/bin/pip
FLASK:=$(VENV)/bin/flask

help:
	@echo "Available targets:"
	@echo "  install     Create a virtualenv and install dependencies"
	@echo "  run         Start the Flask development server"
	@echo "  shell       Open a Flask shell"
	@echo "  db-init     Initialize database migrations"
	@echo "  db-migrate  Generate a migration"
	@echo "  db-upgrade  Apply migrations"
	@echo "  clean       Remove the virtualenv"

$(VENV)/bin/activate: requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install: $(VENV)/bin/activate
	@echo "Virtual environment ready in $(VENV)"

run: $(VENV)/bin/activate
	FLASK_APP=wsgi FLASK_ENV=development $(FLASK) run --debug

shell: $(VENV)/bin/activate
	FLASK_APP=wsgi $(FLASK) shell

db-init: $(VENV)/bin/activate
	FLASK_APP=wsgi $(FLASK) db init

db-migrate: $(VENV)/bin/activate
	FLASK_APP=wsgi $(FLASK) db migrate -m "$(message)"

db-upgrade: $(VENV)/bin/activate
	FLASK_APP=wsgi $(FLASK) db upgrade

clean:
	rm -rf $(VENV)
