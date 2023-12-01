# Use the official Python image as the base image
FROM python:3.13

# Set the working directory in the container
WORKDIR /

# Install the application dependencies
RUN pip install -r requirements.txt

# Define the entry point for the container
CMD ["python", "moobot.py", "runserver", "0.0.0.0:8000"]