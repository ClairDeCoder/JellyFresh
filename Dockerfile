# Base image
FROM python:3.11-slim

# ENV Var for logs
ENV PYTHONUNBUFFERED=1

# Working dir
WORKDIR /app

# Copy code base
COPY . /app

# Make config directory
RUN mkdir -p /opt/jellyfresh

# Install dependencies
RUN pip install --upgrade pip
# Requirements
RUN pip install --no-cache-dir -r requirements.txt
# CVE
RUN pip install --upgrade setuptools

# Expose port 7007
EXPOSE 7007

# Run the app using Gunicorn, no timeout for container
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7007", "--timeout", "0", "main:app"]
