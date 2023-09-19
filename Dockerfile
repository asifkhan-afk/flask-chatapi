# Stage 1: Build the Flask application
FROM python:3.8-slim as build

# Set environment variables for Flask
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Create and set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Stage 2: Create a separate Docker container for the SQLite database
FROM jitesoft/sqlite as db

# Copy the SQLite database file into the container
COPY instance/chatapp.db instance/chatapp.db

# Stage 3: Create the final image for the Flask application
FROM build as final

# Expose port 5000 for Flask
EXPOSE 5000

# Start the Flask application
CMD ["python", "run.py"]
