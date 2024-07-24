# Developing Locally

Airbyte development is broken into two activities, connector development and platform development. Connector development
is largely done in Python, though sometimes Java is used for performance reasons. Platform development is done in Java 
and Kotlin. 

## Prerequisites

:::info

Manually switching between different language versions can be difficult. We recommend using a version manager such as [`pyenv`](https://github.com/pyenv/pyenv) or [`jenv`](https://github.com/jenv/jenv).

:::

The following technologies are required to build Airbyte locally.

1. [`Java 21`](https://jdk.java.net/archive/)
2. `Node 20.`
3. `Python 3.9`
4. `Docker`
5. `Jq`

You should also follow the [Quickstart](../../using-airbyte/getting-started/oss-quickstart.md) to install `abctl`. In 
addition to `abctl` you should also install [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installing-from-release-binaries) 
as well as [Kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl)

If you are looking to build connectors, you should also follow the installation instructions for [airbyte-ci](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)

## Connector Contributions

1. [Fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the [`airbyte`](https://github.com/airbytehq/airbyte) repository.
2. Clone the fork on your workstation:

```bash
git clone git@github.com:{YOUR_USERNAME}/airbyte.git
cd airbyte
```

- Then, build the connector image:
    - Install our [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md) tool to build your connector.
    - Running `airbyte-ci connectors --name source-<source-name> build` will build your connector image.
    - Once the command is done, you will find your connector image in your local docker host: `airbyte/source-<source-name>:dev`.

You can then load the newly built image into the `abctl` instance using:

```shell
kind load docker-image airbyte/source-<source-name>:dev -n airbyte-abctl
```

:::info

The above connector image is tagged with `dev`. You can change this to use another tag if you'd like.

:::

- In your browser, visit [http://localhost:8000/](http://localhost:8000/)
- Log in
- Go to `Settings` (gear icon in lower left corner)
- Go to `Sources` or `Destinations` (depending on which connector you are testing)
- Update the version number to use your docker image tag (default is `dev`)
- Click `Change` to save the changes

Now when you run a sync with that connector, it will use your local docker image


### Connector Specification Caching

The Airbyte Server caches connector specifications for performance reasons. If you update the specification of a 
connector, you will need to clear this cache so the new changes are registered. To do this:

- In your browser, visit [http://localhost:8000/](http://localhost:8000/)
- Log in
- Go to `Settings` (gear icon in lower left corner)
- Go to `Sources` or `Destinations` (depending on which connector you are testing)
- Update the version number to most recent release docker image tag, e.g. `1.6.4`
- Click `Change` to save the changes
- Set the version back to `dev`
- Click `Change` to save the changes

## Platform Contributions
1. [Fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the [ `airbyte-platform`](https://github.com/airbytehq/airbyte-platform) repository.
2. Clone the fork on your workstation:

```bash
git clone git@github.com:{YOUR_USERNAME}/airbyte-platform.git
cd airbyte-platform
docker compose up
```


To start contributing:


If developing connectors, you can work on connectors locally but additionally start the platform independently locally using :

```bash
git clone git@github.com:{YOUR_USERNAME}/airbyte.git
cd airbyte
./run-ab-platform.sh
```

If developing platform:

```bash
git clone git@github.com:{YOUR_USERNAME}/airbyte-platform.git
cd airbyte-platform
docker compose up
```

### Build with `gradle`

To compile and build the platform, run the following command in your local `airbyte-platform` repository:

```bash
./gradlew build
```

This will build all the code and run all the unit tests.

`./gradlew build` creates all the necessary artifacts \(Webapp, Jars and Docker images\) so that you can run Airbyte locally. Since this builds everything, it can take some time.

:::info

Optionally, you may pass a `VERSION` environment variable to the gradle build command. If present, gradle will use this value as a tag for all created artifacts (both Jars and Docker images).

If unset, gradle will default to using the current VERSION in `.env` for Jars, and `dev` as the Docker image tag.

:::
:::info

If running tasks on a subproject, you must prepend `:oss` to the project in gradlew. For example, to build the `airbyte-cron` project the command would look like: `./gradlew :oss:airbyte-cron:build`.

:::

:::info

Gradle will use all CPU cores by default. If Gradle uses too much/too little CPU, tuning the number of CPU cores it uses to better suit a dev's need can help.

Adjust this by either, 1. Setting an env var: `export GRADLE_OPTS="-Dorg.gradle.workers.max=3"`. 2. Setting a cli option: `./gradlew build --max-workers 3` 3. Setting the `org.gradle.workers.max` property in the `gradle.properties` file.

A good rule of thumb is to set this to \(\# of cores - 1\).

:::

:::info

On Mac, if you run into an error while compiling openssl \(this happens when running pip install\), you may need to explicitly add these flags to your bash profile so that the C compiler can find the appropriate libraries.

```bash
export LDFLAGS="-L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I/usr/local/opt/openssl/include"
```

:::


### Develop on `airbyte-webapp`

- Spin up Airbyte locally in your local `airbyte-platform` repository so the UI can make requests against the local API.

```bash
BASIC_AUTH_USERNAME="" BASIC_AUTH_PASSWORD="" docker compose up
```

Note: [basic auth](https://docs.airbyte.com/operator-guides/security#network-security) must be disabled by setting `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD` to empty values, otherwise requests from the development server will fail against the local API.

- Install [`nvm`](https://github.com/nvm-sh/nvm) (Node Version Manager) if not installed
- Use `nvm` to install the required node version:

```bash
cd airbyte-webapp
nvm install
```

- Install the `pnpm` package manager in the required version. You can use Node's [corepack](https://nodejs.org/api/corepack.html) for that:

```bash
corepack enable && corepack install
```

- Start up the react app.

```bash
pnpm install
pnpm start
```

### Run platform acceptance tests

In your local `airbyte-platform` repository, run the following commands to run acceptance \(end-to-end\) tests for the platform:

```bash
./gradlew clean build
./gradlew :oss:airbyte-tests:acceptanceTests
```

Test containers start Airbyte locally, run the tests, and shutdown Airbyte after running the tests. If you want to run acceptance tests against local Airbyte that is not managed by the test containers, you need to set `USE_EXTERNAL_DEPLOYMENT` environment variable to true:

```bash
USE_EXTERNAL_DEPLOYMENT=true ./gradlew :oss:airbyte-tests:acceptanceTests
```

## Formatting code

Airbyte runs a code formatter as part of the build to enforce code styles. You should run the formatter yourself before submitting a PR (otherwise the build will fail).

The command to run formatting varies slightly depending on which part of the codebase you are working in.

### Platform

If you are working in the platform run `./gradlew format` from the root of the `airbyte-platform` repository.

### Connector

To format your local `airbyte` repository, run `airbyte-ci format fix all`.

## Troubleshooting

### Resetting the Airbyte developer environment

Sometimes you'll want to reset the data in your local environment. One common case for this is if you are updating an connector's entry in the database \(`airbyte-config-oss/init-oss/src/main/resources/config`\), often the easiest thing to do, is wipe the local database and start it from scratch. To reset your data back to a clean install of Airbyte, follow these steps:

- Make sure you are in your local `airbyte-platform` repository

- Delete the datastore volumes in docker

```bash
abctl local uninstall --persisted
```

- Remove the data on disk

```bash
rm -rf ~/.airbyte/
```

- Rebuild the project

```bash
./gradlew clean build
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

### Could not target platform: 'Java SE 14' using tool chain: 'JDK 8 (1.8)'.

Somehow gradle didn't pick up the right java version for some reason. Find the install version and set the `JAVA_HOME` environment to point to the JDK folder.

For example:

```text
env JAVA_HOME=/usr/lib/jvm/java-14-openjdk ./gradlew  :airbyte-integrations:connectors:your-connector-dir:build
```

### Inspecting the messages passed between connectors

From your local `airbyte-platform` repository, you can enable `LOG_CONNECTOR_MESSAGES=true` to log the messages the Airbyte platform receives from the source and destination when debugging locally. e.g. `LOG_CONNECTOR_MESSAGES=true VERSION=dev docker compose up`
