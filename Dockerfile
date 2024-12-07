# Use the alpine lsio image as a base image
FROM ghcr.io/linuxserver/baseimage-alpine:3.20

# Owner Github
LABEL maintainer="cyb3rgh05t"
LABEL org.opencontainers.image.source="https://github.com/cyb3rgh05t/discord-bot"

# Set timezone environment variable
ENV TZ=Europe/Berlin

# Update packages and install dependencies
RUN apk update && apk upgrade && apk add --no-cache \
        python3 \
        py3-pip \
        tini \
        wget \
        tzdata \
        libffi-dev \
        openssl-dev \
    && rm -rf /var/cache/apk/*

# Create and activate a virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir \
    discord.py \
    discord-py-slash-command \
    py-discord-html-transcripts \
    aiohttp \
    captcha \
    pillow \
    PyNaCl \
    asyncio \
    psutil

# Copy the s6-overlay run script and other necessary files
COPY ./root/ /

# Define mount points for config and databases
VOLUME /config
VOLUME /databases

# Use tini as the init system
ENTRYPOINT ["/sbin/tini", "--"]
