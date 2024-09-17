# Use the official Python image from the Docker Hub
FROM python:3.12

USER thash


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the Docker container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install the dependencies from the requirements file
RUN pip install --root --upgrade pip && pip install --root -r requirements.txt

# Copy the Django application code to the container
COPY . /app/

# Expose the port the Django app runs on
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
