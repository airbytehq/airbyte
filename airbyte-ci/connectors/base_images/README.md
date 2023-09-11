# airbyte-connectors-base-images

This python package contains the base images used by Airbyte connectors.
It is intended to be used as a python library.
Our connector build pipeline ([`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1)) **will** use this library to build the connector images.
Our base images are declared in code, using the [Dagger Python SDK](https://dagger-io.readthedocs.io/en/sdk-python-v0.6.4/).

## Base images


### `airbyte/python-connector-base`

| Version | Date | Changelog | 
|---------|------|-----------|
|  1.0.0 | 2023-09-19 | Initial release: an image based on python:3.9.18-slim-bookworm with pip==23.2.1 and poetry==1.6.1 |


## Where are the Dockerfiles?
Our base images are not declared using Dockerfiles.
They are declared in code using the [Dagger Python SDK](https://dagger-io.readthedocs.io/en/sdk-python-v0.6.4/).
We prefer this approach because it allows us to interact with base images container as code: we can use python to declare the base images and use the full power of the language to build and test them.
However, we do artificially generate Dockerfiles for debugging and documentation purposes:


### Example for `airbyte/python-connector-base`:
```dockerfile
FROM docker.io/python:3.9.18-slim-bookworm@sha256:44b7f161ed03f85e96d423b9916cdc8cb0509fb970fd643bdbc9896d49e1cad0
RUN ln -snf /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN pip install --upgrade pip==23.2.1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VIRTUALENVS_IN_PROJECT=false
ENV POETRY_NO_INTERACTION=1
RUN pip install poetry==1.6.1
```


## How to release a new base image version (example for Python)

1. `poetry install`
2. Open  `base_images/python/bases.py`.
3. Make changes to the `AirbytePythonConnectorBaseImage`, you're likely going to change the `get_container` method to change the base image.
4. Implement the `container` property which must return a `dagger.Container` object.
5. *Recommended*: Add new sanity checks to `run_sanity_check` to confirm that the new version is working as expected.
6. Publish the new base image version by running `poetry run publish`. **Make sure you're logged in to DockerHub** with `docker login`. 
It will:
  - Prompt you to pick which base image you'd like to publish.
  - Prompt you for a major/minor/patch/pre-release version bump.
  - Prompt you for  a changelog message.
  - Run the sanity checks on the new version.
  - Publish the new version to DockerHub.
  - Regenerate the docs and the registry json file.
7. Commit and push your changes.
8. Create a PR and ask for a review from the Connector Operations team.

Please note that:
- No connector will use the new base image version until its metadata is updated to use it.
- If you're not fully confident with the new base image version, please publish it as a pre-release version.

## Running tests locally
```bash
poetry run pytest
# Static typing checks
poetry run mypy base_images --check-untyped-defs
```
