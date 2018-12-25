virtualenv: requirements.txt Makefile
	rm -fr virtualenv/
	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade virtualenv
	python3 -m virtualenv virtualenv
	source ./virtualenv/bin/activate; \
	python3 -m pip install -r requirements.txt

development: test virtualenv
	source ./virtualenv/bin/activate; \
	FLASK_ENV=development FLASK_APP=hikariita flask run

production: test virtualenv
	source ./virtualenv/bin/activate; \
	python3 /root/hikariita/virtualenv/bin/flask run --host=0.0.0.0 --port=80

test: virtualenv
	source ./virtualenv/bin/activate; \
	python3 -m pytest tests/

