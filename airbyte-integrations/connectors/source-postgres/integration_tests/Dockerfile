# Use the official PostgreSQL image from the Docker Hub
FROM postgres:latest

# Set environment variables for the PostgreSQL database
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword
ENV POSTGRES_DB=mydatabase

RUN apt-get update && apt-get install -y postgresql-contrib

# Copy your SQL script into the container
COPY ./seed/init.sql /docker-entrypoint-initdb.d/