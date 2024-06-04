# airbyte-connectors-base-images

This python package contains the base images used by Airbyte connectors.
It is intended to be used as a python library.
Our connector build pipeline ([`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1)) uses this library to build the connector images.
Our base images are declared in code, using the [Dagger Python SDK](https://dagger-io.readthedocs.io/en/sdk-python-v0.6.4/).

- [Python base image code declaration](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/base_images/base_images/python/bases.py)
- ~Java base image code declaration~ *TODO* 


## Where are the Dockerfiles?
Our base images are not declared using Dockerfiles.
They are declared in code using the [Dagger Python SDK](https://dagger-io.readthedocs.io/en/sdk-python-v0.6.4/).
We prefer this approach because it allows us to interact with base images container as code: we can use python to declare the base images and use the full power of the language to build and test them.
However, we do artificially generate Dockerfiles for debugging and documentation purposes.



### Example for `airbyte/python-connector-base`:
```dockerfile
FROM docker.io/python:3.9.19-slim-bookworm@sha256:b92e6f45b58d9cafacc38563e946f8d249d850db862cbbd8befcf7f49eef8209
RUN ln -snf /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN pip install --upgrade pip==24.0 setuptools==70.0.0
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VIRTUALENVS_IN_PROJECT=false
ENV POETRY_NO_INTERACTION=1
RUN pip install poetry==1.6.1
RUN sh -c apt update && apt-get install -y socat=1.7.4.4-2
RUN sh -c apt-get update && apt-get install -y tesseract-ocr=5.3.0-2 poppler-utils=22.12.0-2+b1
RUN mkdir /usr/share/nltk_data
```



## Base images


### `airbyte/python-connector-base`

| Version    | Published | Docker Image Address                                                                                                       | Changelog                                                                                            |
| ---------- | --------- | -------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 1.2.1      | ✅        | docker.io/airbyte/python-connector-base:1.2.1@sha256:4a4255e2bccab71fa5912487e42d9755cdecffae77273fed8be01a081cd6e795      | Upgrade to Python 3.9.19 + update pip and setuptools                                                 |
| 1.2.0      | ✅        | docker.io/airbyte/python-connector-base:1.2.0@sha256:c22a9d97464b69d6ef01898edf3f8612dc11614f05a84984451dde195f337db9      | Add CDK system dependencies: nltk data, tesseract, poppler.                                          |
| 1.2.0-rc.1 | ✅        | docker.io/airbyte/python-connector-base:1.2.0-rc.1@sha256:f6467768b75fb09125f6e6b892b6b48c98d9fe085125f3ff4adc722afb1e5b30 |                                                                                                      |
| 1.1.0      | ✅        | docker.io/airbyte/python-connector-base:1.1.0@sha256:bd98f6505c6764b1b5f99d3aedc23dfc9e9af631a62533f60eb32b1d3dbab20c      | Install socat                                                                                        |
| 1.0.0      | ✅        | docker.io/airbyte/python-connector-base:1.0.0@sha256:dd17e347fbda94f7c3abff539be298a65af2d7fc27a307d89297df1081a45c27      | Initial release: based on Python 3.9.18, on slim-bookworm system, with pip==23.2.1 and poetry==1.6.1 |


## How to release a new base image version (example for Python)

### Requirements
* [Docker](https://docs.docker.com/get-docker/)
* [Poetry](https://python-poetry.org/docs/#installation)
* Dockerhub logins

### Steps
1. `poetry install`
2. Open  `base_images/python/bases.py`.
3. Make changes to the `AirbytePythonConnectorBaseImage`, you're likely going to change the `get_container` method to change the base image.
4. Implement the `container` property which must return a `dagger.Container` object.
5. **Recommended**: Add new sanity checks to `run_sanity_check` to confirm that the new version is working as expected.
6. Cut a new base image version by running `poetry run generate-release`. You'll need your DockerHub credentials.

It will:
  - Prompt you to pick which base image you'd like to publish.
  - Prompt you for a major/minor/patch/pre-release version bump.
  - Prompt you for  a changelog message.
  - Run the sanity checks on the new version.
  - Optional: Publish the new version to DockerHub.
  - Regenerate the docs and the registry json file.
7. Commit and push your changes.
8. Create a PR and ask for a review from the Connector Operations team.

**Please note that if you don't publish your image while cutting the new version you can publish it later with `poetry run publish <repository> <version>`.**
No connector will use the new base image version until its metadata is updated to use it.
If you're not fully confident with the new base image version please:
  - please publish it as a pre-release version
  - try out the new version on a couple of connectors
  - cut a new version with a major/minor/patch bump and publish it
  - This steps can happen in different PRs.


## Running tests locally
```bash
poetry run pytest
# Static typing checks
poetry run mypy base_images --check-untyped-defs
```
