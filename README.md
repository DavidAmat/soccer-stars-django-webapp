# soccer-stars-django-webapp

This is a first commit of the project.

## Environment

```
pyenv virtualenv 3.9.11 env_soccer
pyenv activate env_soccer
python -m pip install -U 'channels[daphne]'
python3 -m pip install channels_redis
# /home/david/.pyenv/versions/env_soccer/bin/python
```

Follow the docs on installation of Channels:
- https://channels.readthedocs.io/en/latest/installation.html

```
python -m django startproject soccer_match
cd soccer_match
python3 manage.py startapp match
```

## Redis

```
# Either in a Docker
docker run --rm -p 6379:6379 redis:7

# or locally
sudo apt update
sudo apt install redis-server
sudo service redis-server start
redis-cli ping
# redis-cli -h 127.0.0.1 -p 6379 ping
# sudo service redis-server stop
```

Communicate with Redis using the Django Redis Channels

### Redis Channels demo in Python

```
python3 manage.py shell
import channels.layers
channel_layer = channels.layers.get_channel_layer()
from asgiref.sync import async_to_sync

# Run this in terminal 1
async_to_sync(channel_layer.send)('test_channel', {'type': 'hello'})


# Run this in terminal 2
async_to_sync(channel_layer.receive)('test_channel')
# {'type': 'hello'}
async_to_sync(channel_layer.receive)('test_channel')
# It will keep waiting until we go to terminal 1 and send another message

# Run this in terminal 1 
async_to_sync(channel_layer.send)('test_channel', {'type': 'hello2'})

# In Terminal 2 you will see 
# {'type': 'hello2'}
```

To decode a serialized message

```
import msgpack

data = b"p\xbe$\xe1\xe8\xca?\xd6l7\xdb?\x81\xa4type\xa6hello9"
string = msgpack.unpackb(data)

```

### WebSocket demo in Python

```
# In the folder server/backend run
daphne -p 8000 backend.asgi:application

# This runs the server and then you can test the websocket with the notebook server/notebooks/websocket/debug_websocket.ipynb
```


# Containerization of the Project

To create Docker containers for both the client and the server, you need to have two separate Dockerfiles: one for the client and one for the server.

## Client

```jsx
# Use an official Node.js runtime as a parent image
FROM node:14

# Set the working directory
WORKDIR /usr/src/app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install the dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"]

```

## Server

```jsx
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
```

Plus, we need to change two things in the Django environment and your Python dependencies:

### Pyproject toml

We started the project with a simple `pyenv` environment. To convert the installed dependencies into a pyproject toml do:

```jsx
pyenv activate env_soccer
pip install poetry
cd server/backend

poetry init
# respond to yes and fill some project names and metadata you are prompted

pip freeze > requirements.txt
cat requirements.txt | xargs -n 1 poetry add
# inside the container it will run poetry install defined in the DOckerfile

```

### Allow Logging

```jsx
# settings.py
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",  # Set to DEBUG to see all logs
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
```

In your code do:

```jsx
import logging

# Get a logger instance
logger = logging.getLogger(__name__)
```

### Set Allowed hosts

```jsx
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "server"]
```

# Docker compose to manage both containers

```jsx
version: '3.8'

services:
  client:
    build:
      context: ./client
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - server
    networks:
      - soccer-network

  server:
    build:
      context: ./server/backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    networks:
      - soccer-network

networks:
  soccer-network:
    driver: bridge

```

## Run docker compose

```jsx
# Build containers
docker compose up --build

# See live logs
docker compose logs -f server
docker compose logs -f client

# Delete containers
docker compose down
```

### Issues with Websocket connection

### Correct WebSocket URL for the Browser

The WebSocket URL must use the appropriate address that the browser can resolve and access. When using Docker Compose, the service name should be used, but from the host's perspective, you need to use `localhost` or the actual IP address of your Docker host.

### Solution Steps

1. **Update the WebSocket URL**:
Use `localhost` instead of `0.0.0.0` for the browser to resolve and access the WebSocket server running in the container.

This is the reason why we can keep:

```jsx
const WEBSOCKET_URL = "ws://localhost:8000/ws/match/";
```

# Running it locally

Open two terminals:

## Terminal 1: The Server

```jsx
pyenv activate env_soccer
cd server/backend
daphne -p 8000 backend.asgi:application
```

## Terminal 2: The Client

```jsx
cd client/
npm start
```