# Use the alpine lsio image as a base image
FROM ghcr.io/linuxserver/baseimage-alpine:3.20

# Owner Github
LABEL maintainer=cyb3rgh05t
LABEL org.opencontainers.image.source=https://github.com/cyb3rgh05t/discord-bot

# Set timezone environment variable
ENV TZ=Europe/Berlin

# Update the package list and install dependencies using apk (Alpine package manager)
RUN apk update && apk upgrade \
    && apk add --no-cache \
        python3 \
        py3-pip \
        tini \
        wget \
        tzdata \
        gcc \
        musl-dev \
        python3-dev \
        linux-headers \
        build-base \
        libffi-dev \
        openssl-dev \
    && rm -rf /var/cache/apk/*  # Clean up after installation

# Install the required Python dependencies directly
RUN pip install --no-cache-dir discord.py \
    discord-py-slash-command \
    py-discord-html-transcripts \
    aiohttp \
    captcha \
    pillow \
    PyNaCl \
    asyncio \
    psutil

# Clean up build tools to reduce image size
RUN apk del gcc musl-dev python3-dev linux-headers build-base

# Copy the s6-overlay run script and other necessary files
COPY ./root/ /

# Define mount points for config and databases
VOLUME /config
VOLUME /databases
