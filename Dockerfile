# Use the alpine lsio image as a base image
FROM ghcr.io/linuxserver/baseimage-alpine:3.20

# Owner Github
LABEL maintainer=cyb3rgh05t
LABEL org.opencontainers.image.source=https://github.com/cyb3rgh05t/discord-bot

ENV TZ=Europe/Berlin

# Install dependencies using apk (Alpine package manager)
RUN apk update && apk upgrade \
    && apk add --no-cache \
        python3 \
        py3-pip \
        tini \
        wget \
        tzdata \
        libffi-dev \
        jpeg-dev \
        zlib-dev \
    && rm -rf /var/cache/apk/*  # Clean up after installation

# Set up a virtual environment to avoid conflicts
RUN python3 -m venv /venv

# Upgrade pip and setuptools in the virtual environment
RUN /venv/bin/pip install --upgrade pip setuptools

# Install Python dependencies in the virtual environment
RUN /venv/bin/pip install --no-cache-dir discord.py discord-py-slash-command \
    py-discord-html-transcripts aiohttp captcha pillow \
    PyNaCl asyncio psutil

# Copy the s6-overlay run script and other necessary files
COPY ./root/ / 

# Define mount points for config and databases
VOLUME /config
VOLUME /databases
