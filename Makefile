# Must set the shell to bash instead of /bin/sh to use 'source'
SHELL := /bin/bash

virtualenv: requirements.txt Makefile
	rm -fr virtualenv/
	python3 -m pip install --user virtualenv
	python3 -m virtualenv virtualenv
	source ./virtualenv/bin/activate && python3 -m pip install -r requirements.txt

development: test virtualenv
	source ./virtualenv/bin/activate && FLASK_ENV=development FLASK_APP=hikariita flask run

production: test virtualenv
	source ./virtualenv/bin/activate && FLASK_APP=hikariita python3 -m flask run --host=0.0.0.0 --port=80 >> log.stdout 2>> log.stderr &

test: virtualenv
	source ./virtualenv/bin/activate && python3 -m pytest pytest_tests/ --junitxml=test_results.xml

backup:
	cp example.db ~/Dropbox/

jenkins:
	wget -q -O - https://pkg.jenkins.io/debian/jenkins-ci.org.key | apt-key add -
	echo deb https://pkg.jenkins.io/debian-stable binary/ | tee /etc/apt/sources.list.d/jenkins.list
	apt-get update
	apt-get install default-jre # Needed for web server that jenkins runs on
	apt-get install docker.io # Needed for docker container management
	apt-get install jenkins
	usermod -a -G docker jenkins # Need to add jenkins user to the docker group so it can talk to docker
	systemctl restart jenkins # Need to restart jenkins after changing permissions above
