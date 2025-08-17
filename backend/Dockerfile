FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive

# Update apt and install necessary packages (e.g., for psycopg2-binary C-dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements.txt first
COPY requirements.txt .

# Install PyTorch for CPU separately to handle large download and potential OOM issues
# Use http:// for index-url to avoid subtle HTTPS errors during Docker build
RUN pip install --no-cache-dir torch==2.0.1 --index-url http://download.pytorch.org/whl/cpu --trusted-host download.pytorch.org
# Use grep -v to filter out torch from the main requirements file before installing the rest
RUN grep -v "torch" requirements.txt > /tmp/requirements_no_torch.txt \
    && pip install --no-cache-dir -r /tmp/requirements_no_torch.txt \
    && rm /tmp/requirements_no_torch.txt

# Copy the application code
COPY ./app /app/app

# Expose the API port
EXPOSE 8000

# Command to run the application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]