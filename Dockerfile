# Use an official Node.js image
FROM node:18-buster-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the TypeScript code
RUN npm run build

# Ensure the audio_files directory exists
RUN mkdir -p audio_files

# Start the bot
CMD ["npm", "run", "start"]
