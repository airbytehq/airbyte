# Step 7: Use the Connector in Airbyte

To use your connector in your own installation of Airbyte, build the docker image for your container by running `docker build . -t airbyte/source-python-http-example:dev`. Then, follow the instructions from the [building a python source tutorial](https://docs.airbyte.io/connector-development/tutorials/building-a-python-source) for using the connector in the Airbyte UI, replacing the name as appropriate.

Note: your built docker image must be accessible to the `docker` daemon running on the Airbyte node. If you're doing this tutorial locally, these instructions are sufficient. Otherwise you may need to push your Docker image to Dockerhub.
