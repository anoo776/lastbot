FROM python:3.10-slim

# Install ffmpeg (needed for yt-dlp to merge video/audio)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of your code
COPY . .

# Run your bot (Change 'bot.py' to your filename if it's different)
CMD ["python", "bot.py"]