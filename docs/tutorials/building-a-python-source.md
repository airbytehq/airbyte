# Building a Python Source

## Summary

This article provides a checklist for how to create a python source. Each step in the checklist has a link to a more detailed explanation below.

## Requirements

Docker, Python, and Java with the versions listed in the [tech stack section](../architecture/tech-stack.md).

{% hint style="info" %}
All the commands below assume that `python` points to a version of python 3. On some systems, `python` points to a Python2 installation and `python3` points to Python3. If this is the case on your machine, substitute all `python` commands in this guide with `python3` . Otherwise, make sure to install Python 3 before beginning.
{% endhint %}

## Checklist

### Creating a Source

* Step 1: Create the source using template
* Step 2: Build the newly generated source `./gradlew :airbyte-integrations:connectors:source-<source-name>:build`
* Step 3: Set up your Airbyte development environment 
* Step 4: Implement `spec` \(and define the specification for the source `airbyte-integrations/connectors/source-<source-name>/spec.json`\)
* Step 5: Implement `check`
* Step 6: Implement `discover`
* Step 7: Implement `read`
* Step 8: Set up Standard Tests
* Step 9: Write unit tests or integration tests
* Step 10: Update the `README.md` \(If API credentials are required to run the integration, please document how they can be obtained or link to a how-to guide.\)
* Step 11: Add the connector to the API/UI \(by adding an entry in `airbyte-config/init/src/main/resources/seed/source_definitions.yaml`\)
* Step 12: Add docs \(in `docs/integrations/sources/<source-name>.md`\)

{% hint style="info" %}
Each step of the Creating a Source checklist is explained in more detail below.
{% endhint %}

{% hint style="info" %}
All `./gradlew` commands must be run from the root of the airbyte project.
{% endhint %}

### Submitting a Source to Airbyte

* If you need help with any step of the process, feel free to submit a PR with your progress and any questions you have. 
* Submit a PR.
* To run integration tests, Airbyte needs access to a test account/environment. Coordinate with an Airbyte engineer \(via the PR\) to add test credentials so that we can run tests for the integration in the CI. \(We will create our own test account once you let us know what source we need to create it for.\)
* Once the config is stored in Github Secrets, edit `.github/workflows/test-command.yml` to inject the config into the build environment.
* Edit the `airbyte/tools/bin/ci_credentials.sh` script to pull the script from the build environment and write it to `secrets/config.json` during the build.
* From the `airbyte` project root, run `./gradlew :airbyte-integrations:connectors:source-<source-name>:build` to make sure your module builds.
* Apply Airbyte auto formatting `./gradlew format` and commit any changes.

{% hint style="info" %}
If you have a question about a step the Submitting a Source to Airbyte checklist include it in your PR or ask it on [slack](https://slack.airbyte.io).
{% endhint %}

## Explaining Each Step

### Step 1: Create the source using template

Airbyte provides a code generator which bootstraps the scaffolding for our connector.

```bash
$ cd airbyte-integrations/connector-templates/generator # assumes you are starting from the root of the Airbyte project.
# Install NPM from https://www.npmjs.com/get-npm if you don't have it
$ npm install
$ npm run generate
```

Select the `python` template and then input the name of your connector. For this walk through we will refer to our source as `example-python`

### Step 2: Build the newly generated source

Build the source using: `./gradlew :airbyte-integrations:connectors:source-<source-name>:build`

This step sets up the initial python environment. By sanity checking that the source builds at the beginning we have a good starting place for developing our source.

### Step 3: Set up your Airbyte development environment

The generator creates a file `source_<source_name>/source.py`. This will be where you implement the logic for your source. The templated `source.py` contains extensive comments explaining each method that needs to be implemented. Briefly here is an overview of each of these methods.

1. `spec`: declares the user-provided credentials or configuration needed to run the connector
2. `check`: tests if with the user-provided configuration the connector can connect with the underlying data source.
3. `discover`: declares the different streams of data that this connector can output
4. `read`: reads data from the underlying data source \(The stock ticker API\)

#### Dependencies

Python dependencies for your source should be declared in `airbyte-integrations/connectors/source-<source-name>/setup.py` in the `install_requires` field. You will notice that a couple of Airbyte dependencies are already declared there. Do not remove these; they give your source access to the helper interface that is provided by the generator.

You may notice that there is a `requirements.txt` in your source's directory as well. Do not touch this. It helps IDEs pull in local Airbyte dependencies to help with code completion. It is _not_ used outside of the development environment. All dependencies should be declared in `setup.py`.

#### Development Environment

Running `./gradlew :airbyte-integrations:connectors:source-<source-name>:build` creates a virtual environment for your source. If you want your IDE to auto complete and resolve dependencies properly, point it at the virtual env `airbyte-integrations/connectors/source-<source-name>/.venv`. Also anytime you change the dependencies in the `setup.py` make sure to re-run the build command. The build system will handle installing all dependencies in the `setup.py` into the virtual environment.

Pretty much all it takes to create a source is to implement the `Source` interface. The template fills in a lot of information for you and has extensive docstrings describing what you need to do to implement each method. The next 4 steps are just implementing that interface.

{% hint style="info" %}
All logging should be done through the `logger` object passed into each method. Otherwise, logs will not be shown in the Airbyte UI.
{% endhint %}

#### Iterating on your implementation

Everyone develops differently but here are 3 ways that we recommend iterating on a source. Consider using whichever one matches your style.

**Run the source using python**

You'll notice in your source's directory that there is a python file called `main_dev.py`. This file exists as convenience for development. You can call it from within the virtual environment mentioned above `. ./.venv/bin/activate` to test out that your source works.

```text
# from airbyte-integrations/connectors/source-<source-name>
python main_dev.py spec
python main_dev.py check --config secrets/config.json
python main_dev.py discover --config secrets/config.json
python main_dev.py read --config secrets/config.json --catalog sample_files/configured_catalog.json
```

The nice thing about this approach is that you can iterate completely within in python. The downside is that you are not quite running your source as it will actually be run by Airbyte. Specifically you're not running it from within the docker container that will house it.

**Run the source using docker**

If you want to run your source exactly as it will be run by Airbyte \(i.e. within a docker container\), you can use the following commands:

```text
# in airbyte root directory
./gradlew :airbyte-integrations:connectors:source-example-python:airbyteDocker
docker run --rm airbyte/source-example-python:dev spec
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-example-python/secrets:/secrets airbyte/source-example-python:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-example-python/secrets:/secrets airbyte/source-example-python:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/airbyte-integrations/connectors/source-example-python/secrets:/secrets -v $(pwd)/airbyte-integrations/connectors/source-example-python/sample_files:/sample_files airbyte/source-example-python:dev read --config /secrets/config.json --catalog /sample_files/configured_catalog.json
```

Note: Each time you make a change to your implementation you need to re-build the connector. `./gradlew :airbyte-integrations:connectors:source-<source-name>:build`. This makes sure that the new python code is added into the docker container.

The nice thing about this approach is that you are running your source exactly as it will be run by Airbyte. The tradeoff is that iteration is slightly slower, because you need to re-build the connector between each change.

**TDD using standard tests**

Airbyte provides a standard test suite that is run against every source. The objective of these tests is to provide some "free" tests that can sanity check that the basic functionality of the source works. One approach to developing your connector is to simply run the tests between each change and use the feedback from them to guide your development.

If you want to try out this approach, check out Step 8 which describes what you need to do to set up the standard tests for your source.

The nice thing about this approach is that you are running your source exactly as Airbyte will run it in the CI. The downside is that the tests do not run very quickly.

### Step 4: Implement `spec`

Each source contains a specification that describes what inputs it needs in order for it to pull data. This file can be found in `airbyte-integrations/connectors/source-<source-name>/spec.json`. This is a good place to start when developing your source. Using JsonSchema define what the inputs are \(e.g. username and password\). Here's [an example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-postgres/src/main/resources/spec.json) of what the `spec.json` looks like for the postgres source.

For more details on what the spec is, you can read about the Airbyte Protocol [here](../architecture/airbyte-specification.md).

The generated code that Airbyte provides, handles implementing the `spec` method for you. It assumes that there will be a file called `spec.json` in the same directory as `source.py`. If you have declared the necessary JsonSchema in `spec.json` you should be done with this step.

### Step 5: Implement `check`

As described in the template code, this method takes in a json object called config that has the values described in the `spec.json` filled in. In other words if the `spec.json` said that the source requires a `username` and `password` the config object might be `{ "username": "airbyte", "password": "password123" }`. It returns a json object that reports, given the credentials in the config, whether we were able to connect to the source. For example, with the given credentials could the source connect to the database server.

While developing, we recommend storing this object in `secrets/config.json`. All tests assume that is where credentials will be stored.

### Step 6: Implement `discover`

As described in the template code, this method takes in the same config object as `check`. It then returns a json object called a `catalog` that describes what data is available and metadata on what options are available for how to replicate it.

For a brief overview on the catalog check out [Beginner's Guide to the Airbyte Catalog](beginners-guide-to-catalog.md).

### Step 7: Implement `read`

As described in the template code, this method takes in the same config object as the previous methods. It also takes in a "configured catalog". This object wraps the catalog emitted by the `discover` step and includes configuration on how the data should be replicated. For a brief overview on the configured catalog check out [Beginner's Guide to the Airbyte Catalog](beginners-guide-to-catalog.md). It then returns each record that it fetches from the source as a stream \(or generator\).

### Step 8: Set up Standard Tests

The Standard Tests are a set of tests that run against all sources. These tests are run in the Airbyte CI to prevent regressions. They also can help you sanity check that your source works as expected. The following [article](../contributing-to-airbyte/building-new-connector/testing-connectors.md) gives a brief overview of the Standard Tests and explains what you need to do to set up these tests.

You can run the tests using `./gradlew :airbyte-integrations:connectors:source-<source-name>:integrationTest`

{% hint style="info" %}
In some rare cases we make exceptions and allow a source to not need to pass all the standard tests. If for some reason you think your source cannot reasonably pass one of the tests cases, reach out to us on github or slack, and we can determine whether there's a change we can make so that the test will pass or if we should skip that test for your source.
{% endhint %}

### Step 9: Write unit tests and/or integration tests

The Standard Tests are meant to cover the basic functionality of a source. Think of it as the bare minimum required for us to add a source to Airbyte.

#### Unit Tests

Add any relevant unit tests to the `unit_tests` directory. Unit tests should _not_ depend on any secrets.

You can run the tests using `./gradlew :airbyte-integrations:connectors:source-<source-name>:test`

#### Integration Tests

_coming soon_

#### Step 10: Update the `README.md`

The template fills in most of the information for the readme for you. Unless there is a special case, the only piece of information you need to add is how one can get the credentials required to run the source. e.g. Where one can find the relevant API key, etc.

#### Step 11: Add the connector to the API/UI

Open the following file: `airbyte-config/init/src/main/resources/seed/source_definitions.yaml`. You'll find a list of all the connectors that Airbyte displays in the UI. Pattern match to add your own connector. Make sure to generate a new _unique_ UUIDv4 for the `sourceDefinitionId` field. You can get one [here](https://www.uuidgenerator.net/). After you do, run `./gradlew :airbyte-config:init:build` \(this command generates some necessary configuration files\).

#### Step 12: Add docs

Each connector has its own documentation page. By convention, that page should have the following path: in `docs/integrations/sources/<source-name>.md`. For the documentation to get packaged with the docs, make sure to add a link to it in `docs/SUMMARY.md`. You can pattern match doing that from existing connectors.

