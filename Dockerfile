FROM ghcr.io/d4vinci/scrapling:latest

WORKDIR /app

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
