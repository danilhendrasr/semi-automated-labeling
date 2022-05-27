# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.234.0/containers/ubuntu/.devcontainer/base.Dockerfile

# [Choice] Ubuntu version (use ubuntu-22.04 or ubuntu-18.04 on local arm64/Apple Silicon): ubuntu-22.04, ubuntu-20.04, ubuntu-18.04
ARG VARIANT="jammy"
FROM mcr.microsoft.com/vscode/devcontainers/base:0-${VARIANT}

ENV DEBIAN_FRONTEND noninteractive

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get update && apt-get --no-install-recommends install -y build-essential \
  curl git redis-server python3-dev python3-pip python3-venv python3-tk software-properties-common && \
  curl -sL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs && \
  add-apt-repository -y ppa:deadsnakes/ppa && add-apt-repository -y ppa:jonathonf/ffmpeg-4 && \
  apt-get install -y ffmpeg libldap2-dev libsasl2-dev pkg-config libavformat-dev libavcodec-dev \
  libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev \
  python3.9 python3.9-distutils python3.9-dev