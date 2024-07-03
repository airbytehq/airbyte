# Use a base image with PostgreSQL client
FROM ubuntu:latest

# Install any additional packages if needed
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the script to the container
COPY script.sh .
COPY init.sql .

# Give execution rights to the script
RUN chmod +x script.sh
