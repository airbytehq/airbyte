FROM node

# We change to a directory unique to us
WORKDIR /airbyte/integration_code
# Install any needed Python dependencies
RUN npm install yargs
# Copy source files
COPY source.js .
COPY spec.json .

# When this container is invoked, append the input argemnts to `python source.py`
ENTRYPOINT ["node", "/airbyte/integration_code/source.js"]

# Airbyte's build system uses these labels to know what to name and tag the docker images produced by this Dockerfile.
LABEL io.airbyte.name=airbyte/source-chandler
LABEL io.airbyte.version=0.1.0

# In order to launch a source on Kubernetes in a pod, we need to be able to wrap the entrypoint.
# The source connector must specify its entrypoint in the AIRBYTE_ENTRYPOINT variable.
ENV AIRBYTE_ENTRYPOINT='node /airbyte/integration_code/source.js'
