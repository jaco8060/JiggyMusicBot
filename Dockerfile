# Use an official Node.js image
FROM node:18-buster-slim

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Ensure the audio_files directory exists
RUN mkdir -p audio_files

# Expose necessary ports (if any)
EXPOSE 3000

# Start the bot
CMD ["npm", "run", "start"]
