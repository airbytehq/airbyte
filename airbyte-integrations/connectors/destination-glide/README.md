# Glide Destination

This is the repository for the Glide destination connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/destinations/glide).

## Development

The active todo list is at [./todo.md].
The gist of the Glide-specific code is in `/destination_glide/destination.py` and `/destination_glide/glide.py`.

### Prerequisites

- Python (`^3.9`, tested recently with `3.12.3`)
- Poetry (`^1.7`, tested recently with `1.8.3_1`)

I used homebrew for installing these prerequisites on macOS.

### Unit Tests

The unit tests for that code are in `/destination-glide/unit_tests`. To run them run:

```sh
./scripts/test-unit.sh
```

### Integration Tests

The destination has a configuration in `/secrets/config.json`. That file must confirm to the configuration specification in `/destination_glide/spec.json`. It should be something like:

```json
{
  "api_host": "http://localhost:5005",
  "api_path_root": "api",
  "api_key": "decafbad-1234-1234-1234-decafbad"
}
```

The spec also specifies the configuration UI within the Airbyte product itself for configuring the destination.

There are a set of simple integration tests that Airbyte provides that can be triggered with the following scripts:

```sh
./scripts/dev-check.sh
./scripts/dev-spec.sh
./scripts/dev-write.sh
```

These simply call commands that Airbyte provides in their connector template. The dev-write one appears to be the most comprehensive, but I've struggled to get that one to consistently run (see TODO).

### Build & Deployment

The Airbyte destination is packed as Docker image. This script uses Airbyte-provided tooling named `airbyte-ci` that leverages the same tooling they use in their CI pipeline to build the container.

To install the tooling see [`airbyte-ci` README in this repo](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) This worked for me other than to make it work on macOS with homebrew-provided python, I don't have `python` on my path only `python3` so I had to change that in a couple places in the `Makefile` in the root of this repo.

```sh
./scripts/build-docker-image.sh
```

We are currently deploying this to a public repository for ease of access from an Airbyte OSS instance. To deploy it to a docker container registry use the script at:

```sh
./scripts/push-docker-image.sh
```

### Running in Airbyte OSS Locally

To install Airbyte follow the guide at https://docs.airbyte.com/deploying-airbyte/quickstart. On macOS this uses homebrew to install k8s kind locally and get an airbyte cluster running. It took a while but worked smoothly for me. I am currently using `airbytehq/tap/abctl (0.5.0)`.

Once install it should be available at http://localhost:8000/. You should have been prompted for username/pw during install.

### Installing Glide Destination in Airbyte OSS

To install the destination into Airbyte OSS follow these steps:

1. Click on **Settings** on the far left then select **Destinations** in the sub-panel. You should see a list of **Available destination connectors**.
2. At the top click the **+ New Connector** button fill in the fields. The **Docker repository name** and **Docker image tag** are the important bits.

Once installed, you can upgrade it to a new version by visiting the same settings page and changing the tag in the **Change to** box and clicking the **Change** button.

---

## Old (from Airbyte's Template)

### Installing the connector

From this connector directory, run:

```bash
poetry install --with dev
```

#### Create credentials

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/destinations/glide)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `destination_glide/spec.json` file.
Note that the `secrets` directory is gitignored by default, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `destination glide test creds`
and place them into `secrets/config.json`.

### Locally running the connector

```
poetry run destination-glide spec
poetry run destination-glide check --config secrets/config.json
poetry run destination-glide write --config secrets/config.json --catalog sample_files/configured_catalog.json
```

### Running tests

To run tests locally, from the connector directory run:

```
poetry run pytest tests
```

### Building the docker image

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run the following command to build the docker image:

```bash
airbyte-ci connectors --name=destination-glide build
```

An image will be available on your host with the tag `airbyte/destination-glide:dev`.

### Running as a docker container

Then run any of the connector commands as follows:

```
docker run --rm airbyte/destination-glide:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-glide:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-glide:dev write --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

### Running our CI test suite

You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):

```bash
airbyte-ci connectors --name=destination-glide test
```

### Customizing acceptance Tests

Customize `acceptance-test-config.yml` file to configure acceptance tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.

### Dependency Management

All of your dependencies should be managed via Poetry.
To add a new dependency, run:

```bash
poetry add <package-name>
```

Please commit the changes to `pyproject.toml` and `poetry.lock` files.

## Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?

1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=destination-glide test`
2. Bump the connector version (please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors)):
   - bump the `dockerImageTag` value in in `metadata.yaml`
   - bump the `version` value in `pyproject.toml`
3. Make sure the `metadata.yaml` content is up to date.
4. Make sure the connector documentation and its changelog is up to date (`docs/integrations/destinations/glide.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
8. Once your PR is merged, the new version of the connector will be automatically published to Docker Hub and our connector registry.
