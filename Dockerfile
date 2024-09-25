# Use an official Node.js image for ARM architectures (e.g., Raspberry Pi)
FROM node:18-buster-slim

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy the rest of the application code
COPY . .

# Expose necessary ports (if any)
EXPOSE 3000

# Start the bot
CMD ["npm", "run", "start"]
