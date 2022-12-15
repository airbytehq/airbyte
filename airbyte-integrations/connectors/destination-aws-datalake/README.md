# Aws Datalake Destination

This is the repository for the Aws Datalake destination connector, written in Python.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.io/integrations/destinations/aws-datalake).

## Local development

### Prerequisites

**To iterate on this connector, make sure to complete this prerequisites section.**

#### Minimum Python version required `= 3.7.0`

#### Build & Activate Virtual Environment and install dependencies

From this connector directory, create a virtual environment:

```bash
python -m venv .venv
```

This will generate a virtualenv for this module in `.venv/`. Make sure this venv is active in your
development environment of choice. To activate it from the terminal, run:

```bash
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

```bash
./gradlew :airbyte-integrations:connectors:destination-aws-datalake:build
```

#### Create credentials

**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.io/integrations/destinations/aws-datalake)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `destination_aws_datalake/spec.json` file.
Note that the `secrets` directory is gitignored by default, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `destination aws-datalake test creds`
and place them into `secrets/config.json`.

### Locally running the connector

```bash
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

### Locally running the connector docker image

#### Build

First, make sure you build the latest Docker image:

```bash
docker build . -t airbyte/destination-aws-datalake:dev
```

You can also build the connector image via Gradle:

```bash
./gradlew :airbyte-integrations:connectors:destination-aws-datalake:airbyteDocker
```

When building via Gradle, the docker image name and tag, respectively, are the values of the `io.airbyte.name` and `io.airbyte.version` `LABEL`s in
the Dockerfile.

#### Run

Then run any of the connector commands as follows:

```bash
docker run --rm airbyte/destination-aws-datalake:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/destination-aws-datalake:dev check --config /secrets/config.json
# messages.jsonl is a file containing line-separated JSON representing AirbyteMessages
cat messages.jsonl | docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/destination-aws-datalake:dev write --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```

## Testing

Make sure to familiarize yourself with [pytest test discovery](https://docs.pytest.org/en/latest/goodpractices.html#test-discovery) to know how your test files and methods should be named.

First install test dependencies into your virtual environment:

```bash
pip install .[tests]
```

### Unit Tests

To run unit tests locally, from the connector directory run:

```bash
python -m pytest unit_tests
```

### Integration Tests

There are two types of integration tests: Acceptance Tests (Airbyte's test suite for all destination connectors) and custom integration tests (which are specific to this connector).

#### Custom Integration tests

Place custom tests inside `integration_tests/` folder, then, from the connector root, run

```bash
python -m pytest integration_tests
```

#### Acceptance Tests

Coming soon:

### Using gradle to run tests

All commands should be run from airbyte project root.
To run unit tests:

```bash
./gradlew :airbyte-integrations:connectors:destination-aws-datalake:unitTest
```

To run acceptance and custom integration tests:

```bash
./gradlew :airbyte-integrations:connectors:destination-aws-datalake:integrationTest
```

#### Running the Destination Acceptance Tests

To successfully run the Destination Acceptance Tests, you need a `secrets/config.json` file with appropriate information. For example:

```json
{
    "bucket_name": "your-bucket-name",
    "bucket_prefix": "your-prefix",
    "region": "your-region",
    "aws_account_id": "111111111111",
    "lakeformation_database_name": "an_lf_database",
    "credentials": {
      "credentials_title": "IAM User",
      "aws_access_key_id": ".....",
      "aws_secret_access_key": "....."
    }
}
```

In the AWS account, you need to have the following elements in place:

* An IAM user with appropriate IAM permissions (Notably S3 and Athena)
* A Lake Formation database pointing to the configured S3 location (See: [Creating a database](https://docs.aws.amazon.com/lake-formation/latest/dg/creating-database.html))
* An Athena workspace named `AmazonAthenaLakeFormation` where the IAM user has proper authorizations
* The user must have appropriate permissions to the Lake Formation database to perform the tests (For example see: [Granting Database Permissions Using the Lake Formation Console and the Named Resource Method](https://docs.aws.amazon.com/lake-formation/latest/dg/granting-database-permissions.html))



## Dependency Management

All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.

We split dependencies between two groups, dependencies that are:

* required for your connector to work need to go to `MAIN_REQUIREMENTS` list.
* required for the testing need to go to `TEST_REQUIREMENTS` list

### Publishing a new version of the connector

You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?

1. Make sure your changes are passing unit and integration tests.
1. Bump the connector version in `Dockerfile` -- just increment the value of the `LABEL io.airbyte.version` appropriately (we use [SemVer](https://semver.org/)).
1. Create a Pull Request.
1. Pat yourself on the back for being an awesome contributor.
1. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.
