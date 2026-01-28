# Use the official lightweight Python image.
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt


# Copy project files
COPY . /app/
# Ensure the CSV file is present before import
COPY "DAILYTRACKING.csv" /app/

# Expose port for Flask
EXPOSE 10000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Database setup
#RUN flask db init || true
#RUN python create_tables.py
#RUN python importcsv.py

# Run the application
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
