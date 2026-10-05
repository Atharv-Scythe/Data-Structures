FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . .

# Set Python Path
ENV PYTHONPATH=/app

# Expose Flask API Port
EXPOSE 5000

CMD ["python", "app.py"]
