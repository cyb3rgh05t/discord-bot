# Use the alpine lsio image as a base image
FROM ghcr.io/linuxserver/baseimage-alpine:3.20

# Owner Github
LABEL maintainer=cyb3rgh05t
LABEL org.opencontainers.image.source=https://github.com/cyb3rgh05t/discord-bot

ENV TZ=Europe/Berlin

# Update the package list and install dependencies
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y \
        python3 \
        python3-pip \
        tini \
        wget \
        tzdata \
    && apt-get clean

RUN pip install --no-cache-dir discord.py discord-py-slash-command \
    py-discord-html-transcripts aiohttp captcha pillow \
    PyNaCl asyncio psutil

# Copy the s6-overlay run script and other necessary files
COPY ./root/ /

VOLUME /config
VOLUME /databases