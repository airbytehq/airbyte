# Developing Locally

## Develop with `gradle`

Dataline uses `java 14` and `node 14`

To compile the code and run unit tests:

```bash
git clone git@github.com:datalineio/dataline.git
cd dataline
./gradlew clean build
```

This will build all the code and run all the unit tests

## Run with `docker-compose`

```bash
./gradlew composeBuild
VERSION=dev docker-compose up
```

The build will take a few minutes. Once it completes, Dataline compiled at current git revision will be running in your environment.

## Run Acceptance Tests

To run acceptance \(end-to-end\) tests you must have the Dataline running locally. 

```bash
./gradlew composeBuild
VERSION=dev docker-compose up
./gradlew :dataline-tests:acceptanceTests
```

## Develop on individual applications

### Develop on `dataline-webapp`

1. First we'll set up the rest of the Dataline backend so that the UI can be making requests against the Dataline APIs instead of mocking everything out.

```bash
docker-compose up -d server scheduler
```

2. Start up the react app.

```bash
cd dataline-webapp
npm install
npm start
```

### Develop on `dataline-server` \(APIs\)

This section will describe how to run the API using Gradle. It is geared towards iterating quickly on the API; it trades off not setting up all of the dependencies for speed.

1. First we need to setup up local version of the Scheduler Store. We'll run it it in a docker a container using the following command:

```bash
docker-compose up -d scheduler
```

2. Now we'll set up the Config Store and seed it with some data. We're just going to throw this in your tmp dir.

```bash
mkdir -p /tmp/dataline
cp -r dataline-config/init/src/main/resources/* /tmp/dataline
```

3. Now let's run the server. This command takes care of compiling the API, so every time you use this command it will be running with whatever is current version of the code.

```bash
./gradlew :dataline-server:run
```

4. And now you're ready to go! Make sure everything is working by testing out a call to the API

```bash
curl -H "Content-Type: application/json"\
 -X POST localhost:8001/api/v1/workspaces/get\
 -d '{ "workspaceId": "5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6" }'
```

_Note: We namespace most API calls with a workspace id. For now there is only ever one workspace that is hardcoded to the id used in this example. If you ever need a workspace id, just use this one._

### Develop on `dataline-scheduler`

1. First we need to setup up local version of the Scheduler Store. We'll run it it in a docker a container using the following command:

```bash
docker-compose up -d db
```

2. Now we'll set up the Config Store and seed it with some data. We're just going to throw this in your tmp dir.

```bash
mkdir -p /tmp/dataline
cp -r dataline-config/init/src/main/resources/* /tmp/dataline
```

3. Now let's run the server. This command takes care of compiling the API, so every time you use this command it will be running with whatever is current version of the code.

```bash
./gradlew :dataline-scheduler:run
```

