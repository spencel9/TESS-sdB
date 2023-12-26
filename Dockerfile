# Use the official Python image as the base image
FROM python:3.8

# Set the working directory within the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install the Python packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the entrypoint shell script into the container at /app
COPY docker-entrypoint.sh .

# Make the shell script executable
RUN sudo chmod +x docker-entrypoint.sh

# Specify the entry point for the container
ENTRYPOINT ["./docker-entrypoint.sh"]
