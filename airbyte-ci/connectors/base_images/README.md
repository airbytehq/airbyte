# airbyte-connectors-base-images

This python package contains the base images used by Airbyte connectors.
It is intended to be used as a python library.
Our connector build pipeline ([`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1)) uses this library to build the connector images.
Our base images are declared in code, using the [Dagger Python SDK](https://dagger-io.readthedocs.io/en/sdk-python-v0.15.3/).

- [Python base image code declaration](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/base_images/base_images/python/bases.py)
- [Java base image code declaration](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/base_images/base_images/java/bases.py)


## Where are the Dockerfiles?
Our base images are not declared using Dockerfiles.
They are declared in code using the [Dagger Python SDK](https://dagger-io.readthedocs.io/en/sdk-python-v0.15.3/).
We prefer this approach because it allows us to interact with base images container as code: we can use python to declare the base images and use the full power of the language to build and test them.
However, we do artificially generate Dockerfiles for debugging and documentation purposes.



### Example for `airbyte/python-connector-base`:
```dockerfile
FROM docker.io/python:3.10.14-slim-bookworm@sha256:2407c61b1a18067393fecd8a22cf6fceede893b6aaca817bf9fbfe65e33614a3
RUN ln -snf /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN adduser --uid 1000 --system --group --no-create-home airbyte
RUN mkdir --mode 755 /custom_cache
RUN mkdir --mode 755 /airbyte
RUN chown airbyte:airbyte /airbyte
ENV PIP_CACHE_DIR=/custom_cache/pip
RUN pip install --upgrade pip==24.0 setuptools==70.0.0
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VIRTUALENVS_IN_PROJECT=false
ENV POETRY_NO_INTERACTION=1
RUN pip install poetry==1.6.1
RUN sh -c apt-get update && apt-get upgrade -y && apt-get dist-upgrade -y && apt-get clean
RUN sh -c apt-get install -y socat=1.7.4.4-2
RUN sh -c apt-get update && apt-get install -y tesseract-ocr=5.3.0-2 poppler-utils=22.12.0-2+b1
RUN mkdir -p 755 /usr/share/nltk_data
```



### Example for `airbyte/java-connector-base`:
```dockerfile
FROM docker.io/amazoncorretto:21-al2023@sha256:c90f38f8a5c4494cb773a984dc9fa9a727b3e6c2f2ee2cba27c834a6e101af0d
RUN sh -c set -o xtrace && yum install -y shadow-utils tar openssl findutils && yum update -y --security && yum clean all && rm -rf /var/cache/yum && groupadd --gid 1000 airbyte && useradd --uid 1000 --gid airbyte --shell /bin/bash --create-home airbyte && mkdir /secrets && mkdir /config && mkdir --mode 755 /airbyte && mkdir --mode 755 /custom_cache && chown -R airbyte:airbyte /airbyte && chown -R airbyte:airbyte /custom_cache && chown -R airbyte:airbyte /secrets && chown -R airbyte:airbyte /config && chown -R airbyte:airbyte /usr/share/pki/ca-trust-source && chown -R airbyte:airbyte /etc/pki/ca-trust && chown -R airbyte:airbyte /tmp
ENV AIRBYTE_SPEC_CMD=/airbyte/javabase.sh --spec
ENV AIRBYTE_CHECK_CMD=/airbyte/javabase.sh --check
ENV AIRBYTE_DISCOVER_CMD=/airbyte/javabase.sh --discover
ENV AIRBYTE_READ_CMD=/airbyte/javabase.sh --read
ENV AIRBYTE_WRITE_CMD=/airbyte/javabase.sh --write
ENV AIRBYTE_ENTRYPOINT=/airbyte/base.sh
```



## Base images


### `airbyte/python-connector-base`

| Version | Published | Docker Image Address | Changelog | 
|---------|-----------|--------------|-----------|
|  3.0.2 | ✅| docker.io/airbyte/python-connector-base:3.0.2@sha256:73697fbe1c0e2ebb8ed58e2268484bb4bfb2cb56b653808e1680cbc50bafef75 |  |
|  3.0.1-rc.1 | ✅| docker.io/airbyte/python-connector-base:3.0.1-rc.1@sha256:5b5cbe613691cc61d643a347ee4ba21d6358252f274ebb040ef820c7b9f4a5a7 |  |
|  3.0.0 | ✅| docker.io/airbyte/python-connector-base:3.0.0@sha256:1a0845ff2b30eafa793c6eee4e8f4283c2e52e1bbd44eed6cb9e9abd5d34d844 | Create airbyte user |
|  3.0.0-rc.1 | ✅| docker.io/airbyte/python-connector-base:3.0.0-rc.1@sha256:ee046486af9ad90b1b248afe5e92846b51375a21463dff1cd377c4f06abb55b5 | Update Python 3.10.4 image + create airbyte user |
|  2.0.0 | ✅| docker.io/airbyte/python-connector-base:2.0.0@sha256:c44839ba84406116e8ba68722a0f30e8f6e7056c726f447681bb9e9ece8bd916 | Use Python 3.10 |
|  1.2.3 | ✅| docker.io/airbyte/python-connector-base:1.2.3@sha256:a8abfdc75f8e22931657a1ae15069e7b925e74bb7b5ef36371a85e4caeae5696 | Use latest root image version and update system packages |
|  1.2.2 | ✅| docker.io/airbyte/python-connector-base:1.2.2@sha256:57703de3b4c4204bd68a7b13c9300f8e03c0189bffddaffc796f1da25d2dbea0 | Fix Python 3.9.19 image digest |
|  1.2.2-rc.1 | ✅| docker.io/airbyte/python-connector-base:1.2.2-rc.1@sha256:a8abfdc75f8e22931657a1ae15069e7b925e74bb7b5ef36371a85e4caeae5696 | Create an airbyte user and use it |
|  1.2.1 | ✅| docker.io/airbyte/python-connector-base:1.2.1@sha256:4a4255e2bccab71fa5912487e42d9755cdecffae77273fed8be01a081cd6e795 | Upgrade to Python 3.9.19 + update pip and setuptools |
|  1.2.0 | ✅| docker.io/airbyte/python-connector-base:1.2.0@sha256:c22a9d97464b69d6ef01898edf3f8612dc11614f05a84984451dde195f337db9 | Add CDK system dependencies: nltk data, tesseract, poppler. |
|  1.2.0-rc.1 | ✅| docker.io/airbyte/python-connector-base:1.2.0-rc.1@sha256:f6467768b75fb09125f6e6b892b6b48c98d9fe085125f3ff4adc722afb1e5b30 |  |
|  1.1.0 | ✅| docker.io/airbyte/python-connector-base:1.1.0@sha256:bd98f6505c6764b1b5f99d3aedc23dfc9e9af631a62533f60eb32b1d3dbab20c | Install socat |
|  1.0.0 | ✅| docker.io/airbyte/python-connector-base:1.0.0@sha256:dd17e347fbda94f7c3abff539be298a65af2d7fc27a307d89297df1081a45c27 | Initial release: based on Python 3.9.18, on slim-bookworm system, with pip==23.2.1 and poetry==1.6.1 |


### `airbyte/java-connector-base`

| Version | Published | Docker Image Address | Changelog | 
|---------|-----------|--------------|-----------|
|  2.0.1 | ✅| docker.io/airbyte/java-connector-base:2.0.1@sha256:ec89bd1a89e825514dd2fc8730ba299a3ae1544580a078df0e35c5202c2085b3 | Bump Amazon Coretto image version for compatibility with Apple M4 architecture. |
|  2.0.0 | ✅| docker.io/airbyte/java-connector-base:2.0.0@sha256:5a1a21c75c5e1282606de9fa539ba136520abe2fbd013058e988bb0297a9f454 | ~Release non root base image~ |
|  2.0.0-rc.2 | ✅| docker.io/airbyte/java-connector-base:2.0.0-rc.2@sha256:e5543b3de4c38e9ef45dba886bad5ee319b0d7bfe921f310c788f1d4466e25eb | Fine tune permissions and reproduce platform java base implementation |
|  2.0.0-rc.1 | ✅| docker.io/airbyte/java-connector-base:2.0.0-rc.1@sha256:484b929684b9e4f60d06cde171ee0b8238802cb434403293fcede81c1e73c537 |  Make the java base image non root |
|  1.0.0 | ✅| docker.io/airbyte/java-connector-base:1.0.0@sha256:be86e5684e1e6d9280512d3d8071b47153698fe08ad990949c8eeff02803201a | Create a base image for our java connectors based on Amazon Corretto. |
|  1.0.0-rc.4 | ✅| docker.io/airbyte/java-connector-base:1.0.0-rc.4@sha256:be86e5684e1e6d9280512d3d8071b47153698fe08ad990949c8eeff02803201a | Bundle yum calls in a single RUN |
|  1.0.0-rc.3 | ✅| docker.io/airbyte/java-connector-base:1.0.0-rc.3@sha256:be86e5684e1e6d9280512d3d8071b47153698fe08ad990949c8eeff02803201a |  |
|  1.0.0-rc.2 | ✅| docker.io/airbyte/java-connector-base:1.0.0-rc.2@sha256:fca66e81b4d2e4869a03b57b1b34beb048e74f5d08deb2046c3bb9919e7e2273 | Set entrypoint to base.sh |
|  1.0.0-rc.1 | ✅| docker.io/airbyte/java-connector-base:1.0.0-rc.1@sha256:886a7ce7eccfe3c8fb303511d0e46b83b7edb4f28e3705818c090185ba511fe7 | Create a base image for our java connectors. |


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
6. Cut a new base image version by running `dagger run --silent poetry run generate-release`. You'll need your DockerHub credentials.

It will:
  - Prompt you to pick which base image you'd like to publish.
  - Prompt you for a major/minor/patch/pre-release version bump.
  - Prompt you for a changelog message.
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

## CHANGELOG

### 1.4.0
- Declare a base image for our java connectors.

### 1.3.1
- Update the crane image address. The previous address was deleted by the maintainer.

### 1.2.0
- Improve new version prompt to pick bump type with optional pre-release version.

### 1.1.0
- Add a cache ttl for base image listing to avoid DockerHub rate limiting.

### 1.0.4
- Upgrade Dagger to `0.13.3`

### 1.0.2

- Improved support for images with non-semantic-versioned tags.

### 1.0.1

- Bumped dependencies ([#42581](https://github.com/airbytehq/airbyte/pull/42581))
