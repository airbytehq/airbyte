# Developing Locally

Airbyte development is broken into two activities, connector development and platform development. Connector development
is largely done in Python by community contributors, though sometimes Java is used for performance reasons. Platform development is done in Java
and Kotlin. In addition to the Java and Kotlin code, the Platform also consists of the UI. The UI is developed in
TypeScript using React.

## Submitting Code

If you would like to submit code to Airbyte, please follow the [Pull Request Handbook](resources/pull-requests-handbook.md)
guide when creating Github Pull Requests. When you are ready to submit code, use the [Submit a New Connector](submit-new-connector.md) document to make
sure that the process can go as smoothly as possible.

## Prerequisites

:::info

Manually switching between different language versions can be difficult. We recommend using a version manager such as [`pyenv`](https://github.com/pyenv/pyenv) or [`jenv`](https://github.com/jenv/jenv).

:::

The following technologies are required to build Airbyte locally.

1. [`Java 21`](https://jdk.java.net/archive/)
2. `Node 20`
3. `Python 3.10`
4. `Docker`
5. `Jq`

If you are looking to build connectors, you should also follow the installation instructions for [airbyte-ci](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md).

### Using abctl for Airbyte development

The guides in this document explain how to develop Connectors and the Airbyte Platform with `abctl`. You should
follow the [Quickstart](../using-airbyte/getting-started/oss-quickstart.md) instructions to install `abctl`.

[Kubernetes in Docker](https://kind.sigs.k8s.io/) (`kind`) is used by `abctl` to create a local Kubernetes cluster as a docker container.
Once the `kind` cluster has been created, `abctl` then uses [Helm](https://helm.sh/) along with the [Airbyte Chart](https://github.com/airbytehq/airbyte-platform/tree/main/charts)
to deploy Airbyte. In order to view logs, debug issues, and managed your Airbyte deployment, you should install the
[kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installing-from-release-binaries) command line tools, as well as,
[kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl) for interacting with the Kubernetes cluster.

To configure your `kubectl` client so that it can communicate with your `abctl` cluster, run the following:

```shell
kind export kubeconfig -n airbyte-abctl
```

You can then view any issues with the pods (deployed containers) by running:

```shell
kubectl get pods -n airbyte-abctl
```

Which should output something like:

```shell
NAME                                                     READY   STATUS      RESTARTS        AGE
airbyte-abctl-airbyte-bootloader                         0/1     Completed   0               4h20m
airbyte-abctl-connector-builder-server-55bc78bd-6sxdp    1/1     Running     0               4h20m
airbyte-abctl-cron-b48bccb78-jnz7b                       1/1     Running     0               4h20m
airbyte-abctl-pod-sweeper-pod-sweeper-599fd8f56d-kj5t9   1/1     Running     0               4h20m
airbyte-abctl-server-74465db7fd-gk25q                    1/1     Running     0               4h20m
airbyte-abctl-temporal-bbb84b56c-jh8x7                   1/1     Running     0               4h33m
airbyte-abctl-webapp-745c949464-brpjf                    1/1     Running     0               4h20m
airbyte-abctl-worker-79c895c7dc-ssqvc                    1/1     Running     0               4h20m
airbyte-db-0                                             1/1     Running     0               4h34m
airbyte-minio-0                                          1/1     Running     0               4h34m
```

Viewing logs for a particular pod can be done by running:

```shell
kubectl logs -n airbyte-abctl airbyte-abctl-server-74465db7fd-gk25q
```

## Connector Contributions

1. [Fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the [`airbyte`](https://github.com/airbytehq/airbyte) repository.
2. Clone the fork on your workstation:

```bash
git clone git@github.com:{YOUR_USERNAME}/airbyte.git
cd airbyte
```

3. Make sure that `abctl` is running correctly with the following command `abctl local status`. Verify the status check
was successful

4. Then, build the connector image:
    - Verify the `airbyte-ci` tool is installed by running `airbyte-ci --help`, install the command with the instructions in the Prerequisites if the command is not found.
    - Run `airbyte-ci connectors --name source-<source-name> build` will build your connector image.
    - Once the command is done, you will find your connector image in your local docker host: `airbyte/source-<source-name>:dev`.

5. Verify the image was published locally by running:

```shell
docker images ls | grep airbyte/source-<source-name>:dev
```

You should see output similar to:
```shell
airbyte/destination-s3 | dev | 70516a5908ce | 2 minutes ago | 968MB
```

6. You can then load the newly built image into the `abctl` instance using:

```shell
kind load docker-image airbyte/source-<source-name>:dev -n airbyte-abctl
```

:::info

The above connector image is tagged with `dev`. You can change this to use another tag if you'd like via the `docker image tag` command.

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
- Leave the version set to `dev`
- Click `Change` to save the changes, which will refresh the dev connectors spec

## Platform Contributions
1. [Fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the [ `airbyte-platform`](https://github.com/airbytehq/airbyte-platform) repository.
2. Clone the fork on your workstation:

```bash
git clone git@github.com:{YOUR_USERNAME}/airbyte-platform.git
cd airbyte-platform
```

3. Make sure that `abctl` is running correctly with the following command `abctl local status`. Verify the status check
was successful

### Build with `gradle`

To compile and build the platform, run the following command in your local `airbyte-platform` repository:

```bash
./gradlew build
```

This will build all the code and run all the unit tests.

`./gradlew build` creates all the necessary artifacts \(Webapp, Jars, and Docker images\) so that you can run Airbyte locally. Since this builds everything, it can take some time.


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

### Using the images in abctl

Once you have successfully built the Platform images, you can load them into the `abctl` Kind cluster, for example:

```shell
kind load docker-image airbyte/server:dev --name airbyte-abctl
```

Adjust the image for the Airbyte component that you would like to test. Then you can adjust your vaulues.yaml file to
use the `dev` tag for the component, e.g.

```shell
server:
  image:
    tag: dev
```

Then redeploy `abctl` by running:

```shell
abctl local install --values values.yaml
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

## Webapp Contributions

To develop features in the Airbyte Webapp, you must first bring up an instance of Airbyte on TCP port 8001. To do this
using `abctl`, first follow the [Quickstart](../using-airbyte/getting-started/oss-quickstart.md) to install `abctl`. Then run the following:

```bash
abctl local install --port 8001
```

### Disabling Authentication

It may be convenient to turn off authentication. If you wish to turn off authentication, create a new text file named:
`values.yaml` and copy the follow into the file:

```yaml
global:
  auth:
    enabled: false
```

Then you can run `abctl` with the following:

```bash
abctl local install --port 8001 --values ./values.yaml
```

### Installing Dependencies

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

### Running the Webapp

- Start up the react app.

```bash
pnpm install
pnpm start
```

## Formatting code

Airbyte runs a code formatter as part of the build to enforce code styles. You should run the formatter yourself before submitting a PR (otherwise the build will fail).

The command to run formatting varies slightly depending on which part of the codebase you are working in.

### Connector

We wrapped all our code formatting tools in [airbyte-ci](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md).
Follow the instructions on the `airbyte-ci` page to install `airbyte-ci`.

You can run `airbyte-ci format fix all` to format all the code your local `airbyte` repository.
We wrapped this command in a pre-push hook so that you can't push code that is not formatted.

To install the pre-push hook, run:

```bash
make tools.pre-commit.setup
```

This will install `airbyte-ci` and the pre-push hook.

The pre-push hook runs formatting on all the repo files.
If the hook attempts to format a file that is not part of your contribution, it means that formatting is also broken in
the master branch. Please open a separate PR to fix the formatting in the master branch.

### Platform

If you are working in the platform run `./gradlew format` from the root of the `airbyte-platform` repository.

## Troubleshooting

### Resetting the Airbyte developer environment

Sometimes you'll want to reset the data in your local environment. One common case for this is if you are updating an connector's entry in the database \(`airbyte-config-oss/init-oss/src/main/resources/config`\), often the easiest thing to do, is wipe the local database and start it from scratch. To reset your data back to a clean install of Airbyte, follow these steps:

- Make sure you are in your local `airbyte-platform` repository

- Delete the datastore volumes in docker

```bash
abctl local uninstall --persisted
```

- Remove the `abctl` data on disk

```bash
rm -rf ~/.airbyte/
```

- Rebuild the project

```bash
./gradlew clean build
abctl local install --values values.yaml
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

[//]: # (### Inspecting the messages passed between connectors)

[//]: # ()
[//]: # (From your local `airbyte-platform` repository, you can enable `LOG_CONNECTOR_MESSAGES=true` to log the messages the Airbyte platform receives from the source and destination when debugging locally. e.g. `LOG_CONNECTOR_MESSAGES=true VERSION=dev docker compose up`)
