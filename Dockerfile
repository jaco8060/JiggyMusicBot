# Dockerfile
# Use the Alpine base image for a lightweight container
FROM python:3.10-alpine

# Install FFmpeg, Opus, and other necessary packages with no-cache for a smaller image size
RUN apk add --no-cache ffmpeg opus

# Install Poetry for dependency management
RUN pip install --no-cache-dir poetry

# Set the working directory in the container
WORKDIR /app

# Copy only the dependency files to the container to leverage Docker caching
COPY pyproject.toml poetry.lock ./

# Install project dependencies using Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev --no-interaction --no-ansi

# Copy the rest of the application files
COPY . .

# Ensure the audio_files directory exists
RUN mkdir -p audio_files

# Command to run the bot
CMD ["poetry", "run", "python", "-m", "bot.main"]
