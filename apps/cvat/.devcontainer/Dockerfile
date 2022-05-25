# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.234.0/containers/ubuntu/.devcontainer/base.Dockerfile

# [Choice] Ubuntu version (use ubuntu-22.04 or ubuntu-18.04 on local arm64/Apple Silicon): ubuntu-22.04, ubuntu-20.04, ubuntu-18.04
ARG VARIANT="jammy"
FROM mcr.microsoft.com/vscode/devcontainers/base:0-${VARIANT}

# [Optional] Uncomment this section to install additional OS packages.
RUN apt-get update && apt-get --no-install-recommends install -y build-essential \
  curl git redis-server python3-dev python3-pip python3-venv python3-tk \ 
  libldap2-dev libsasl2-dev pkg-config libavformat-dev libavcodec-dev \ 
  libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev
