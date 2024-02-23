# Step 7: Use the Connector in Airbyte

To use your connector in your own installation of Airbyte you have to build the docker image for your connector. 



**Option A: Building the docker image with `airbyte-ci`**

This is the preferred method for building and testing connectors.

If you want to open source your connector we encourage you to use our [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) tool to build your connector. 
It will not use a Dockerfile but will build the connector image from our [base image](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/base_images/README.md) and use our internal build logic to build an image from your Python connector code.

Running `airbyte-ci connectors --name source-<source-name> build` will build your connector image.
Once the command is done, you will find your connector image in your local docker host: `airbyte/source-<source-name>:dev`.



**Option B: Building the docker image with a Dockerfile**

If you don't want to rely on `airbyte-ci` to build your connector, you can build the docker image using your own Dockerfile. This method is not preferred, and is not supported for certified connectors.

Create a `Dockerfile` in the root of your connector directory. The `Dockerfile` should look something like this:
```Dockerfile

FROM airbyte/python-connector-base:1.1.0

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```

Please use this as an example. This is not optimized.

Build your image:
```bash
docker build . -t airbyte/source-example-python:dev
```

Then, follow the instructions from the [building a Python source tutorial](../building-a-python-source.md#step-11-add-the-connector-to-the-api-ui) for using the connector in the Airbyte UI, replacing the name as appropriate.

Note: your built docker image must be accessible to the `docker` daemon running on the Airbyte node. If you're doing this tutorial locally, these instructions are sufficient. Otherwise you may need to push your Docker image to Dockerhub.

