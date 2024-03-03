# Use the official Python image as a base image
FROM python:3.9-slim
# Install gcc and python3-dev
RUN apt-get update && apt-get install -y gcc python3-dev

# Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Expose port 5000 to the outside world
EXPOSE 5001

# Command to run the Flask application
CMD ["python", "app.py"]
