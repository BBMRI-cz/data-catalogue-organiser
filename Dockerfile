FROM bitnami/python:3.10

RUN mkdir /organisation-app

WORKDIR /organisation-app

ADD requirements.txt .
ADD main.py .
ADD organiser/ organiser/
ADD tests/ tests/

RUN pip install -r requirements.txt

USER 1005