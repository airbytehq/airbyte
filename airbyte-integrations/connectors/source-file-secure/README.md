# File Source Secure
This is the repository for the File source connector, written in Python. 
This is modificaion of another connector Source File. This version has only one difference with the origin version is this one doesn't support local file storages and is orientated for cloud and cluster platforms.
More details about dependencies and requirement are available [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-file/README.md)

#### Build & Activate Virtual Environment and install dependencies
From this connector directory, create a virtual environment:
```
python -m venv .venv
```

This will generate a virtualenv for this module in `.venv/`. Make sure this venv is active in your
development environment of choice. To activate it from the terminal, run:
```
source .venv/bin/activate
pip install -r requirements.txt
```
If you are in an IDE, follow your IDE's instructions to activate the virtualenv.

Note that while we are installing dependencies from `requirements.txt`, you should only edit `setup.py` for your dependencies. `requirements.txt` is
used for editable installs (`pip install -e`) to pull in Python dependencies from the monorepo and will call `setup.py`.
If this is mumbo jumbo to you, don't worry about it, just put your deps in `setup.py` but install using `pip install -r requirements.txt` and everything
should work as you expect.

#### Building via Gradle
From the Airbyte repository root, run:
```
./gradlew :airbyte-integrations:connectors:source-file-secure:build
```

#### Create credentials
Details are explained [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-file/README.md#create-credentials)

Note that the `secrets` directory is gitignored by default, so there is no danger of accidentally checking in sensitive information.
See `sample_files/sample_config.json` for a sample config file.



**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source file test creds`
and place them into `secrets/config.json`.


### Locally running the connector
```
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
python main.py read --config secrets/config.json --catalog sample_files/configured_catalog.json
```

### Unit Tests
To run unit tests locally, from the connector directory run:
```
python -m pytest unit_tests
```

### Locally running the connector docker image

#### Build
First, make sure you build the latest Docker image:
```
docker build . -t airbyte/source-file-secure:dev \
&& python -m pytest -p connector_acceptance_test.plugin
```

You can also build the connector image via Gradle:
```
./gradlew :airbyte-integrations:connectors:source-file-secure:airbyteDocker
```
When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-file-secure:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-file-secure:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-file-secure:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/sample_files:/sample_files airbyte/source-file-secure:dev read --config /secrets/config.json --catalog /sample_files/configured_catalog.json
```

### Integration Tests
1. From the airbyte project root, run `./gradlew :airbyte-integrations:connectors:source-file-secure:integrationTest` to run the standard integration test suite.
1. To run additional integration tests, place your integration tests in a new directory `integration_tests` and run them with `python -m pytest -s ../source-file/integration_tests`.
   Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.

## Dependency Management
All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing unit and integration tests
1. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use SemVer).
1. Create a Pull Request
1. Pat yourself on the back for being an awesome contributor
1. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master
