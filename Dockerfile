FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/
COPY frontend/ ./frontend/

# Create directory for SQLite database
RUN mkdir -p /app/data

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:////app/data/ai_qa_agent.db

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
