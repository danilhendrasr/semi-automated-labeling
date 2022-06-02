FROM python:3.9.13-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq && \
    apt-get install -y git vim libgtk2.0-dev zip unzip && \
    rm -rf /var/cache/apk/*

RUN pip --no-cache-dir install gitpython
RUN pip --no-cache-dir install streamlit
RUN pip --no-cache-dir install streamlit-option-menu
RUN pip --no-cache-dir install dvc[azure]
RUN pip --no-cache-dir install dvc[gdrive]