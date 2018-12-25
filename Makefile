virtualenv: requirements.txt Makefile
	rm -fr virtualenv/
	python -m pip install --upgrade pip
	python -m virtualenv virtualenv
	source ./virtualenv/bin/activate; \
	python -m pip install -r requirements.txt

development: test virtualenv
	source ./virtualenv/bin/activate; \
	FLASK_ENV=development FLASK_APP=hikariita flask run

production: test virtualenv
	source ./virtualenv/bin/activate; \
	python /root/hikariita/virtualenv/bin/flask run --host=0.0.0.0 --port=80

test: virtualenv
	source ./virtualenv/bin/activate; \
	python -m pytest tests/

