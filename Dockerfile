FROM ghcr.io/d4vinci/scrapling:latest

WORKDIR /app

# Apply distro security updates available in the browser/runtime base image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends --only-upgrade openssl libssl3t64 \
    && apt-get purge -y --auto-remove xvfb xserver-common x11-xkb-utils \
    && rm -rf /app/.venv /usr/bin/uv /usr/bin/uvx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/

# Install extra requirements (FastAPI, Uvicorn for the REST API)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app/

EXPOSE 8000

# Reset entrypoint from base image to allow running uvicorn directly
ENTRYPOINT []

# Run the FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
