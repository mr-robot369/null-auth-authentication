FROM python:3.8

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django application
COPY . .

# Set environment variables (if needed)
# ENV DJANGO_SETTINGS_MODULE=your_project_name.settings

EXPOSE 8000
