FROM node:23

LABEL maintainer=cyb3rgh05t
LABEL org.opencontainers.image.source https://github.com/cyb3rgh05t/discord-bot

# Create the bot's directory
WORKDIR /app/bot/

COPY package*.json ./

# Install dependencie
RUN apt-get update && apt-get install -qq build-essential libcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev g++ software-properties-common
RUN npm install -g
RUN npm install --force --production

COPY . .

# Start the bot.
CMD ["node", "."]
