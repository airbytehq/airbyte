# Developing Locally

The following technologies are required to build Airbyte locally.

1. [`Java 17`](https://jdk.java.net/archive/)
2. `Node 16`
3. `Python 3.7`
4. `Docker`
5. `Postgresql`
6. `Jq`

{% hint style="info" %}
Manually switching between different language versions can get hairy. We recommend using a version manager such as [`pyenv`](https://github.com/pyenv/pyenv) or [`jenv`](https://github.com/jenv/jenv).
{% endhint %}

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

{% hint style="info" %}
If you're using Mac M1 \(Apple Silicon\) machines, it is possible to compile Airbyte by setting
some additional environment variables:

```bash
export DOCKER_BUILD_PLATFORM=linux/arm64
export DOCKER_BUILD_ARCH=arm64
export ALPINE_IMAGE=arm64v8/alpine:3.14
export POSTGRES_IMAGE=arm64v8/postgres:13-alpine
export JDK_VERSION=17
SUB_BUILD=PLATFORM ./gradlew build
```

There are some known issues (Temporal failing during runs, and some connectors not working). See the [GitHub issue](https://github.com/airbytehq/airbyte/issues/2017) for more information.

{% endhint %}

This will build all the code and run all the unit tests.

`SUB_BUILD=PLATFORM ./gradlew build` creates all the necessary artifacts \(Webapp, Jars and Docker images\) so that you can run Airbyte locally. Since this builds everything, it can take some time.

{% hint style="info" %}
Gradle will use all CPU cores by default. If Gradle uses too much/too little CPU, tuning the number of CPU cores it uses to better suit a dev's need can help.

Adjust this by either, 1. Setting an env var: `export GRADLE_OPTS="-Dorg.gradle.workers.max=3"`. 2. Setting a cli option: `SUB_BUILD=PLATFORM ./gradlew build --max-workers 3` 3. Setting the `org.gradle.workers.max` property in the `gradle.properties` file.

A good rule of thumb is to set this to \(\# of cores - 1\).
{% endhint %}

{% hint style="info" %}
On Mac, if you run into an error while compiling openssl \(this happens when running pip install\), you may need to explicitly add these flags to your bash profile so that the C compiler can find the appropriate libraries.

```text
export LDFLAGS="-L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I/usr/local/opt/openssl/include"
```
{% endhint %}

## Run in `dev` mode with `docker-compose`

These instructions explain how to run a version of Airbyte that you are developing on (e.g. has not been released yet).
```bash
SUB_BUILD=PLATFORM ./gradlew build
VERSION=dev docker-compose up
```

The build will take a few minutes. Once it completes, Airbyte compiled at current git revision will be running in `dev` mode in your environment.

In `dev` mode, all data will be persisted in `/tmp/dev_root`.

## Run acceptance tests

To run acceptance \(end-to-end\) tests, you must have the Airbyte running locally.

```bash
SUB_BUILD=PLATFORM ./gradlew clean build
VERSION=dev docker-compose up
SUB_BUILD=PLATFORM ./gradlew :airbyte-tests:acceptanceTests
```

## Run formatting automation/tests

Airbyte runs a code formatter as part of the build to enforce code styles. You should run the formatter yourself before submitting a PR (otherwise the build will fail).

The command to run formatting varies slightly depending on which part of the codebase you are working in.
### Platform
If you are working in the platform run `SUB_BUILD=PLATFORM ./gradlew format` from the root of the repo.

### Connector
If you are working on an individual connectors run: `./gradlew :airbyte-integrations:<directory the connector is in e.g. source-postgres>:format`.

### Connector Infrastructure
Finally, if you are working in any module in `:airbyte-integrations:bases` or `:airbyte-cdk:python`, run `SUB_BUILD=CONNECTORS_BASE ./gradlew format`.

Note: If you are contributing a Python file without imports or function definitions, place the following comment at the top of your file:

```python
"""
[FILENAME] includes [INSERT DESCRIPTION OF CONTENTS HERE]
"""
```

### Develop on `airbyte-webapp`

* Spin up Airbyte locally so the UI can make requests against the local API.
* Stop the `webapp`.

```bash
docker-compose stop webapp
```

* Start up the react app.

```bash
cd airbyte-webapp
npm install
npm start
```

* Happy Hacking!

### Connector Specification Caching

The Configuration API caches connector specifications. This is done to avoid needing to run Docker everytime one is needed in the UI. Without this caching, the UI crawls. If you update the specification of a connector and need to clear this cache so the API / UI picks up the change, you have two options: 

1. Go to the Admin page in the UI and update the version of the connector. Updating to any version, including the one you're already on, will trigger clearing the cache. 
2. Restart the server by running the following commands:

```bash
VERSION=dev docker-compose down -v
VERSION=dev docker-compose up
```

### Resetting the Airbyte developer environment

Sometimes you'll want to reset the data in your local environment. One common case for this is if you are updating an connector's entry in the database \(`airbyte-config/init/src/main/resources/config`\), often the easiest thing to do, is wipe the local database and start it from scratch. To reset your data back to a clean install of Airbyte, follow these steps:

* Delete the datastore volumes in docker

  ```bash
    VERSION=dev docker-compose down -v
  ```

* Remove the data on disk

  ```bash
    rm -rf /tmp/dev_root
    rm -rf /tmp/airbyte_local
  ```

* Rebuild the project

  ```bash
   SUB_BUILD=PLATFORM ./gradlew clean build
   VERSION=dev docker-compose up -V
  ```

## Troubleshooting

### `gradlew Could not target platform: 'Java SE 14' using tool chain: 'JDK 8 (1.8)'.`

Somehow gradle didn't pick up the right java version for some reason. Find the install version and set the `JAVA_HOME` environment to point to the JDK folder.

For example:

```text
env JAVA_HOME=/usr/lib/jvm/java-14-openjdk ./gradlew  :airbyte-integrations:connectors:your-connector-dir:build
```

