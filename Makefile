# Must set the shell to bash instead of /bin/sh to use 'source'
SHELL := /bin/bash

virtualenv: requirements.txt Makefile
	rm -fr virtualenv/
	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade virtualenv
	python3 -m virtualenv virtualenv
	source ./virtualenv/bin/activate && python3 -m pip install -r requirements.txt

development: test virtualenv
	source ./virtualenv/bin/activate && FLASK_ENV=development FLASK_APP=hikariita flask run

production: test virtualenv
	source ./virtualenv/bin/activate && FLASK_APP=hikariita python3 -m flask run --host=0.0.0.0 --port=80 >> log.stdout 2>> log.stderr &

test: virtualenv
	source ./virtualenv/bin/activate && python3 -m pytest tests/

