#!/bin/bash

# read configs to determine secrets
ls /connector/secrets

# Environment variables for the remote PostgreSQL connection
REMOTE_HOST="your_remote_host"
REMOTE_PORT="your_remote_port"
REMOTE_USER="your_remote_user"
REMOTE_PASSWORD="your_remote_password"
REMOTE_DB="your_remote_database"

# Export the password to use with psql
export PGPASSWORD=$REMOTE_PASSWORD

# Run the SQL commands from the init.sql file
psql -h $REMOTE_HOST -p $REMOTE_PORT -U $REMOTE_USER -d $REMOTE_DB -f /usr/local/bin/init.sql