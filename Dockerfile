FROM python:3.13-slim

# Install system dependencies.
RUN apt-get update && \
    apt-get install -y build-essential curl unzip pkg-config && \
    apt-get clean && \
    rm -rf /var/src/apt/lists/*


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    VENV_PATH="/.venv"

ENV DENO_INSTALL="/usr/local/bin"
ENV PATH="$DENO_INSTALL/bin:$PATH"
ENV PATH="$VENV_PATH/bin:$PATH"

# Install Poetry and Deno
RUN pip install --no-cache-dir poetry \
    && curl -fsSL https://deno.land/install.sh | sh

# Install Node.js and TsLab kernel
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash && \
    apt-get update && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/src/apt/lists/*
RUN npm install -g tslab

# Set the working directory
WORKDIR /app
COPY . .

RUN poetry install

# Expose the Jupyter Notebook port
EXPOSE 8888

# Start as a non-root user.
ARG UID=1000

# Create a non-root user.
RUN useradd -m -u ${UID} -s /bin/bash deno

# Set the non-root user as the default user.
USER ${UID}

# Install the Deno Jupyter kernel.
RUN deno jupyter --unstable --install

# Install TsLab
RUN tslab install --python=.venv/bin/python3

# Start Jupyter labs.
CMD ["poetry", "run", "jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--NotebookApp.token=''", "--notebook-dir=notebook"]
