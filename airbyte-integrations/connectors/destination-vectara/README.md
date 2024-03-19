# Vectara Destination

This is the repository for the Vectara destination connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/destinations/vectara).

## Local development

### Prerequisites
**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.10.0`

### Installing the connector
From this connector directory, run:
```bash
poetry install --with dev
```

#### Create credentials
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/destinations/vectara)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `destination_vectara/spec.json` file.
Note that the `secrets` directory is gitignored by default, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `destination vectara test creds`
and place them into `secrets/config.json`.


### Locally running the connector
```
python main.py spec
python main.py check --config secrets/config.json
python main.py write --config secrets/config.json --catalog integration_tests/configured_catalog.json
```


### Locally running the connector docker image


#### Use `airbyte-ci` to build your connector
The Airbyte way of building this connector is to use our `airbyte-ci` tool.
You can follow install instructions [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1).
Then running the following command will build your connector:

```bash
airbyte-ci connectors --name=destination-vectara build
```
Once the command is done, you will find your connector image in your local docker registry: `airbyte/destination-pinecone:dev`.

#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/destination-vectara:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-vectara:dev check --config /secrets/config.json
# messages.jsonl is a file containing line-separated JSON representing AirbyteMessages
cat messages.jsonl | docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-vectara:dev write --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```
## Testing
   Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.
First install test dependencies into your virtual environment:
```
pip install .[tests]
```
### Unit Tests
To run unit tests locally, from the connector directory run:
```
python -m pytest unit_tests
```

### Integration Tests
There are two types of integration tests: Acceptance Tests (Airbyte's test suite for all destination connectors) and custom integration tests (which are specific to this connector).
#### Custom Integration tests
Place custom tests inside `integration_tests/` folder, then, from the connector root, run
```
python -m pytest integration_tests
```

#### Acceptance Tests
Coming soon: 



## Dependency Management
All of your dependencies should go in `pyproject.toml`.

We split dependencies between two groups, dependencies that are:
* required for your connector to work need to go to `[tool.poetry.dependencies]` list.
* required for the testing need to go to `[tool.poetry.group.dev.dependencies]` list

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=destination-vectara test`
2. Bump the connector version in `metadata.yaml`: increment the `dockerImageTag` value. Please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors).
3. Make sure the `metadata.yaml` content is up to date.
4. Make the connector documentation and its changelog is up to date (`docs/integrations/destinations/vectara.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.

