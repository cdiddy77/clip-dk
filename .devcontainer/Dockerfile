# Use the official Python image as a parent image
FROM mcr.microsoft.com/vscode/devcontainers/python:3.11

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

    # Install Poetry
ENV POETRY_HOME=/home/vscode/.local
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    echo "Poetry version:" && \
    /home/vscode/.local/bin/poetry --version

# Set the Poetry path (adjust for container user setup)
ENV PATH="/home/vscode/.local/bin:$PATH"

# Set the working directory
WORKDIR /workspace

# Copy the current directory contents into the container at /workspace
COPY . /workspace

# Install dependencies
# RUN poetry install

# Set the default command to bash
CMD ["bash"]