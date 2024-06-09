# Use an official Python runtime as a parent image
FROM python:3.9

# Install Poetry
RUN pip install poetry

# Set the working directory
WORKDIR /usr/src/app

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock ./

# Install the dependencies
RUN poetry install

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# This change ensures that Daphne binds to all network interfaces, 
# making it accessible from other Docker containers.
CMD ["poetry", "run", "daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"]

