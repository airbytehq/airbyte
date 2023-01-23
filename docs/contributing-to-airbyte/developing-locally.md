# Developing Locally

The following technologies are required to build Airbyte locally.

1. [`Java 17`](https://jdk.java.net/archive/)
2. `Node 16`
3. `Python 3.9`
4. `Docker`
5. `Jq`

:::info

Manually switching between different language versions can get hairy. We recommend using a version manager such as [`pyenv`](https://github.com/pyenv/pyenv) or [`jenv`](https://github.com/jenv/jenv).

:::

To start contributing:

1. Start by [forking](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the repository
2. Clone the fork on your workstation:

   ```bash
   git clone git@github.com:{YOUR_USERNAME}/airbyte.git
   cd airbyte
   ```

3. You're ready to start!

## Build with `gradle`

To compile and build just the platform \(not all the connectors\):

```bash
SUB_BUILD=PLATFORM ./gradlew build
```

This will build all the code and run all the unit tests.

`SUB_BUILD=PLATFORM ./gradlew build` creates all the necessary artifacts \(Webapp, Jars and Docker images\) so that you can run Airbyte locally. Since this builds everything, it can take some time.

:::info

Optionally, you may pass a `VERSION` environment variable to the gradle build command. If present, gradle will use this value as a tag for all created artifacts (both Jars and Docker images).

If unset, gradle will default to using the current VERSION in `.env` for Jars, and `dev` as the Docker image tag.

:::

:::info

Gradle will use all CPU cores by default. If Gradle uses too much/too little CPU, tuning the number of CPU cores it uses to better suit a dev's need can help.

Adjust this by either, 1. Setting an env var: `export GRADLE_OPTS="-Dorg.gradle.workers.max=3"`. 2. Setting a cli option: `SUB_BUILD=PLATFORM ./gradlew build --max-workers 3` 3. Setting the `org.gradle.workers.max` property in the `gradle.properties` file.

A good rule of thumb is to set this to \(\# of cores - 1\).

:::

:::info

On Mac, if you run into an error while compiling openssl \(this happens when running pip install\), you may need to explicitly add these flags to your bash profile so that the C compiler can find the appropriate libraries.

```text
export LDFLAGS="-L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I/usr/local/opt/openssl/include"
```

:::

## Run in `dev` mode with `docker-compose`

These instructions explain how to run a version of Airbyte that you are developing on (e.g. has not been released yet).

```bash
SUB_BUILD=PLATFORM ./gradlew build
VERSION=dev docker compose up
```

The build will take a few minutes. Once it completes, Airbyte compiled at current git revision will be running in `dev` mode in your environment.

In `dev` mode, all data will be persisted in `/tmp/dev_root`.

## Add a connector under development to Airbyte

These instructions explain how to run a version of an Airbyte connector that you are developing on (e.g. has not been released yet).

- First, build the platform images and run Airbyte:

```bash
SUB_BUILD=PLATFORM ./gradlew build
VERSION=dev docker compose up
```

- Then, build the connector image:
```
docker build ./airbyte-integrations/connectors/<connector-name> -t airbyte/<connector-name>:dev
```

:::info

The above connector image is tagged with `dev`. You can change this to use another tag if you'd like.

:::

- In your browser, visit [http://localhost:8000/](http://localhost:8000/)
- Log in with the default user `airbyte` and default password `password`
- Go to `Settings` (gear icon in lower left corner) 
- Go to `Sources` or `Destinations` (depending on which connector you are testing)
- Update the version number to use your docker image tag (default is `dev`)
- Click `Change` to save the changes

Now when you run a sync with that connector, it will use your local docker image

## Run acceptance tests

To run acceptance \(end-to-end\) tests:

```bash
SUB_BUILD=PLATFORM ./gradlew clean build
SUB_BUILD=PLATFORM ./gradlew :airbyte-tests:acceptanceTests
```

Test containers start Airbyte locally, run the tests, and shutdown Airbyte after running the tests. If you want to run acceptance tests against local Airbyte that is not managed by the test containers, you need to set `USE_EXTERNAL_DEPLOYMENT` environment variable to true:

```bash
USE_EXTERNAL_DEPLOYMENT=true SUB_BUILD=PLATFORM ./gradlew :airbyte-tests:acceptanceTests
```

## Run formatting automation/tests

Airbyte runs a code formatter as part of the build to enforce code styles. You should run the formatter yourself before submitting a PR (otherwise the build will fail).

The command to run formatting varies slightly depending on which part of the codebase you are working in.

### Platform

If you are working in the platform run `SUB_BUILD=PLATFORM ./gradlew format` from the root of the repo.

### Connector

To format an individual connector in python, run:

```
 ./gradlew :airbyte-integrations:connectors:<connector_name>:airbytePythonFormat
```

For instance:

```
./gradlew :airbyte-integrations:connectors:source-s3:airbytePythonFormat
```

To format connectors in java, run `./gradlew format`

### Connector Infrastructure

Finally, if you are working in any module in `:airbyte-integrations:bases` or `:airbyte-cdk:python`, run `SUB_BUILD=CONNECTORS_BASE ./gradlew format`.

Note: If you are contributing a Python file without imports or function definitions, place the following comment at the top of your file:

```python
"""
[FILENAME] includes [INSERT DESCRIPTION OF CONTENTS HERE]
"""
```

### Develop on `airbyte-webapp`

- Spin up Airbyte locally so the UI can make requests against the local API.

```bash
BASIC_AUTH_USERNAME="" BASIC_AUTH_PASSWORD="" docker compose up
```

Note: [basic auth](https://docs.airbyte.com/operator-guides/security#network-security) must be disabled by setting `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD` to empty values, otherwise requests from the development server will fail against the local API.

- Start up the react app.

```bash
cd airbyte-webapp
npm install
npm start
```

- Happy Hacking!

### Connector Specification Caching

The Configuration API caches connector specifications. This is done to avoid needing to run Docker everytime one is needed in the UI. Without this caching, the UI crawls. If you update the specification of a connector and need to clear this cache so the API / UI picks up the change, you have two options:

1. Go to the Admin page in the UI and update the version of the connector. Updating to any version, including the one you're already on, will trigger clearing the cache.
2. Restart the server by running the following commands:

```bash
VERSION=dev docker compose down -v
VERSION=dev docker compose up
```

### Resetting the Airbyte developer environment

Sometimes you'll want to reset the data in your local environment. One common case for this is if you are updating an connector's entry in the database \(`airbyte-config/init/src/main/resources/config`\), often the easiest thing to do, is wipe the local database and start it from scratch. To reset your data back to a clean install of Airbyte, follow these steps:

- Delete the datastore volumes in docker

  ```bash
    VERSION=dev docker compose down -v
  ```

- Remove the data on disk

  ```bash
    rm -rf /tmp/dev_root
    rm -rf /tmp/airbyte_local
  ```

- Rebuild the project

  ```bash
   SUB_BUILD=PLATFORM ./gradlew clean build
   VERSION=dev docker compose up -V
  ```

While not as common as the above steps, you may also get into a position where want to erase all of the data on your local docker server. This is useful if you've been modifying image tags while developing.

```bash
docker system prune -a
docker volume prune
```

If you are working on python connectors, you may also need to reset the `virtualenv` and re-install the connector's dependencies.

```bash
# Assuming you have a virtualenv loaded into your shell
deactivate

# From the connector's directory
# remove the venv directory entirely
rm -rf .venv

# make and activate a new venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Troubleshooting

### `gradlew Could not target platform: 'Java SE 14' using tool chain: 'JDK 8 (1.8)'.`

Somehow gradle didn't pick up the right java version for some reason. Find the install version and set the `JAVA_HOME` environment to point to the JDK folder.

For example:

```text
env JAVA_HOME=/usr/lib/jvm/java-14-openjdk ./gradlew  :airbyte-integrations:connectors:your-connector-dir:build
```

### Inspecting the messages passed between connectors

You can enable `LOG_CONNECTOR_MESSAGES=true` to log the messages the Airbyte platform receives from the source and destination when debugging locally. e.g. `LOG_CONNECTOR_MESSAGES=true VERSION=dev docker compose up`
