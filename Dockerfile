FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80/tcp

CMD FLASK_APP=hikariita python3 -m flask run --host=0.0.0.0 --port=80
