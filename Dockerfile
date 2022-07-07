FROM python:3.9.13-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq && \
    apt-get install -y git vim libgtk2.0-dev zip unzip docker.io && \
    rm -rf /var/cache/apk/*

COPY apps/streamlit/requirements.txt /requirements/streamlit.txt
RUN pip --no-cache-dir install -r /requirements/streamlit.txt

COPY apps/dash/requirements.txt /requirements/dash.txt
RUN pip --no-cache-dir install -r /requirements/dash.txt
