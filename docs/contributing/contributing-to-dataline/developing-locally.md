# Developing Locally

## Develop with Docker

```text
git clone git@github.com:datalineio/dataline.git
cd dataline
docker-compose -f docker-compose.build.yaml build
VERSION=dev docker-compose up
```

The build will take a few minutes. Once it completes, Dataline compiled at current git revision will be running in your environment.

## Running Acceptance Tests

To run acceptance \(end-to-end\) tests you must already have the Dataline application running. See [Develop with Docker](developing-locally.md#develop-with-docker) for instructions. Once the application is running all you need to do is running the acceptance tests using Gradle with the following command:

```text
./gradlew clean build :dataline-tests:acceptanceTests
```

## Develop with Gradle

Dataline uses `java 14` and `node 14`

To compile the code and run unit tests:

```text
./gradlew clean build
```

### Run the frontend separately

1. First we'll set up the rest of the Dataline backend so that the UI can be making requests against the Dataline APIs instead of mocking everything out.

```text
docker-compose up -d db seed server scheduler
```

2. Start up the react app.

```text
yarn // installs all js dependencies.
yarn build
yarn start
```

### Run the APIs separately \(Gradle\)

This section will describe how to run the API using Gradle. It is geared towards iterating quickly on the API; it trades off not setting up all of the dependencies for speed.

1. First we need to setup up local version of the Scheduler Store. We'll run it it in a docker a container using the following command:

```text
docker-compose up -d db
```

2. Now we'll set up the Config Store and seed it with some data. We're just going to throw this in your tmp dir.

```text
mkdir -p /tmp/dataline
cp -r dataline-config/init/src/main/resources/* /tmp/dataline
```

3. Now let's run the server. This command takes care of compiling the API, so every time you use this command it will be running with whatever is current version of the code.

```text
./gradlew :dataline-server:run
```

4. And now you're ready to go! Make sure everything is working by testing out a call to the API

```text
curl -H "Content-Type: application/json"\
 -X POST localhost:8001/api/v1/workspaces/get\
 -d '{ "workspaceId": "5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6" }'
```

_Note: We namespace most API calls with a workspace id. For now there is only ever one workspace that is hardcoded to the id used in this example. If you ever need a workspace id, just use this one._

#### Now that you have the API running, here are a couple other useful things to know...

To get a better sense of what you can do with the API, checkout the [documentation](../../architecture/api.md).

The following endpoints aren't going to be successful because they depend directly on the backend. If you are making a change that touches on of these endpoints, then you'll need to run whole Dataline application. You can follow the instructions in the [Develop with Docker](developing-locally.md#develop-with-docker) section.

```text
localhost:80001/api/v1/source_implementations/check_connection
localhost:80001/api/v1/source_implementations/discover_schema
localhost:80001/api/v1/destination_implementations/check_connection
localhost:80001/api/v1/connections/sync
```

### Run the scheduler separately

1. First we need to setup up local version of the Scheduler Store. We'll run it it in a docker a container using the following command:

```text
docker-compose up -d db
```

2. Now we'll set up the Config Store and seed it with some data. We're just going to throw this in your tmp dir.

```text
mkdir -p /tmp/dataline
cp -r dataline-config/init/src/main/resources/* /tmp/dataline
```

3. Now let's run the server. This command takes care of compiling the API, so every time you use this command it will be running with whatever is current version of the code.

```text
./gradlew :dataline-scheduler:run
```

### Run Unit Tests

You can ways run the tests for the project by running:

```text
./gradlew build
```

## Code Style

‌For all the `java` code we follow Google's Open Sourced [style guide](https://google.github.io/styleguide/).‌

### Configure Java Style for IntelliJ <a id="configure-for-intellij"></a>

First download the style configuration

```text
curl https://github.com/google/styleguide/blob/gh-pages/intellij-java-google-style.xml -o ~/Downloads/intellij-java-google-style.xml
```

Install it in IntelliJ:‌

1. Go to `Preferences > Editor > Code Style`
2. Press the little cog:
   1. `Import Scheme > IntelliJ IDEA code style XML`
   2. Select the file we just downloaded
3. Select `GoogleStyle` in the drop down
4. You're done!

