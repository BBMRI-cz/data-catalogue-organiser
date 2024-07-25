FROM bitnami/python:3.10

ADD requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir /scripts

COPY MiSEQ/* /scripts/

USER 1005