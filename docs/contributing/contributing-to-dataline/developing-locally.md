# Developing Locally

## Build with `gradle`

Dataline uses `java 14` , `node 14` and `Docker`

To compile the code and run unit tests:

```bash
git clone git@github.com:datalineio/dataline.git
cd dataline
./gradlew clean build
```

This will build all the code and run all the unit tests.

`./gradle build` creates all the necessary artifacts \(Webapp, Jars and Docker images\) so that you can run dataline locally.

## Run with `docker-compose`

```bash
./gradlew build
VERSION=dev docker-compose up
```

The build will take a few minutes. Once it completes, Dataline compiled at current git revision will be running in your environment.

Dataline by default uses docker volumes for persisting data. If you'd like all persistence to use your local filesystem do the following instead. 

```bash
./gradlew build
docker-compose --env-file .env.dev -f docker-compose.yaml -f docker-compose.dev.yaml up
```

## Run Acceptance Tests

To run acceptance \(end-to-end\) tests you must have the Dataline running locally.

```bash
./gradlew build
VERSION=dev docker-compose up
./gradlew :dataline-tests:acceptanceTests
```

## Develop on individual applications

### Develop on `dataline-webapp`

* Spin up Dataline locally so the UI can make requests against the local API.

```bash
docker-compose --env-file .env.dev -f docker-compose.yaml -f docker-compose.dev.yaml up -d
```

* Stop the `webapp`.

```bash
docker-compose stop webapp
```

* Start up the react app.

```bash
cd dataline-webapp
npm install
npm start
```

* Happy Hacking!

### Develop on `dataline-server` \(APIs\)

* Spin up Dataline locally.

```bash
docker-compose --env-file .env.dev -f docker-compose.yaml -f docker-compose.dev.yaml up -d
```

* Stop the `server`.

```bash
docker-compose stop server
```

* Run the `server` with the command line. It will build and start a `server` with the current state of the code. You can also start the `server` from your IDE if you need to use a debugger.

```bash
./gradlew :dataline-server:run
```

* Make sure everything is working by testing out a call to the API.

```bash
curl -H "Content-Type: application/json"\
 -X POST localhost:8001/api/v1/workspaces/get\
 -d '{ "workspaceId": "5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6" }'
```

* Happy Hacking!

_Note: We namespace most API calls with a workspace id. For now there is only ever one workspace that is hardcoded to the id used in this example. If you ever need a workspace id, just use this one._

### Develop on `dataline-scheduler`

* Spin up Dataline locally.

```bash
docker-compose --env-file .env.dev -f docker-compose.yaml -f docker-compose.dev.yaml up -d
```

* Stop the `scheduler`.

```bash
docker-compose stop scheduler
```

* Run the `scheduler` with the command line. It will build and start a `scheduler` with the current state of the code. You can also start the `scheduler`from your IDE if you need to use a debugger.

```bash
./gradlew :dataline-scheduler:run
```

* Happy Hacking!

