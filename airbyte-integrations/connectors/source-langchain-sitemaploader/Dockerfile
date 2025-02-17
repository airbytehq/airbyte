# Use the Airbyte Python connector base image.
FROM airbyte/python-connector-base:4.0.0

# Set the working directory inside the container.
WORKDIR /airbyte/integration_code

# Copy only the Poetry project files first for dependency caching.
COPY pyproject.toml poetry.lock* ./

# Install Poetry (if not already available in the base image).
RUN pip install poetry

# Install git to load the modified airbyte-cdk repository
RUN apt-get install -y git

# Configure Poetry to install dependencies in the container's environment (without creating a virtualenv)
RUN poetry install --no-dev

# Copy the rest of your connector code into the container.
COPY . .

ENV AIRBYTE_ENTRYPOINT="python /airbyte/integration_code/main.py"
ENTRYPOINT ["sh", "-c", "$AIRBYTE_ENTRYPOINT"]

# The base image already sets the default entrypoint to run the connector,
# so no need to override AIRBYTE_ENTRYPOINT or ENTRYPOINT unless custom behavior is required.
