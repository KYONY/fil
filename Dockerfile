FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY main.py .

# Create necessary directories
RUN mkdir -p /app/logs /app/tg_bot_session

# Run the bot
CMD ["python", "main.py"]