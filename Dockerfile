FROM bitnami/python:3.10

RUN pip install pandas molgenis-py-client

RUN mkdir /scripts

COPY MiSEQ/* /scripts/

USER 1000