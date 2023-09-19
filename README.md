# flask-chatapi
Dockerized Flask App

This repository contains a Dockerized Flask web application.

Prerequisites

Before you can run this application, you need to have the following tools installed on your system:

- Docker
- Docker Compose

Getting Started

1. Clone this repository to your local machine:

   git clone https://github.com/yourusername/your-repo.git

2. Change to the project directory:

   cd your-repo

3. Build the Docker image:

   docker build -t flask-app .

4. Run the application using Docker Compose:

   docker-compose up

   This will start the Flask app and the associated database.

5. Open your web browser and navigate to http://localhost:5000 to access the Flask application.

Stopping the Application

To stop the application and remove the containers, press Ctrl+C in your terminal to stop the docker-compose up command. Then, run:

docker-compose down

Configuration

You can configure the Flask application and database by modifying the environment variables in the docker-compose.yml file.

License

This project is licensed under the MIT License. See the LICENSE file for details.
