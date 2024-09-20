# Use a lightweight Python image compatible with Raspberry Pi (armv7/arm32) and x86 systems
FROM python:3.10-slim

# Install FFmpeg and other necessary packages
# For Windows compatibility, use the below section with 'apt-get' commented out
RUN apt-get update && apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set the working directory in the container
WORKDIR /app

# Copy the project files to the container
COPY . .

# Install project dependencies using Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Ensure the audio_files directory exists
RUN mkdir -p audio_files

# Expose the port (if using Flask for keep-alive)
EXPOSE 8080

# Command to run the bot
CMD ["poetry", "run", "python", "main.py"]
