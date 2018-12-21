development: test
	FLASK_ENV=development FLASK_APP=hikariita flask run

test:
	python -m pytest tests/

