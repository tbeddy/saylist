FROM python:3.6-alpine

RUN adduser -D saylist

WORKDIR /home/saylist

COPY requirements.txt requirements.txt

RUN apk update
RUN apk add postgresql-libs
RUN apk add --virtual .build-deps gcc musl-dev postgresql-dev

RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn psycopg2

RUN apk --purge del .build-deps

COPY app app
COPY migrations migrations
COPY run.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP run.py

RUN chown -R saylist:saylist ./
USER saylist

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]