# Use a lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ ./backend/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port HF uses
EXPOSE 7860

# Run the app (Hugging Face requires --host 0.0.0.0 and port 7860)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]