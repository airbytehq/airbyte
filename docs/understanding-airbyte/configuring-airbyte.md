# Configuring Airbyte

This section covers how to configure Airbyte, and the various configuration Airbyte accepts.

Configuration is currently via environment variables. See the below section on how to modify these variables.

## Docker Deployments

The recommended way to run an Airbyte Docker deployment is via the Airbyte repo's `docker-compose.yaml` and `.env` file.

In this manner, modifying the `.env` file is all that is needed. The `docker-compose.yaml` file injects appropriate variables into the containers. 

If you want to manage your own docker files, please look at the existing docker file to ensure applications get the correct variables.

## Kubernetes Deployments

The recommended way to run an Airbyte Kubernetes deployment is via the 


## Reference

The following  
