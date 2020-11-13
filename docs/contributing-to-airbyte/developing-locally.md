# Developing Locally

Airbyte uses `java 14` , `node 14` and `docker`

To start contributing:

1. Start by [forking](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the repository
2. Clone the fork on your workstation:

   ```bash
   git clone git@github.com:{YOUR_USERNAME}/airbyte.git
   cd airbyte
   ```

3. You're ready to start!

## Build with `gradle`

To compile the code and run unit tests:

```bash
./gradlew clean build
```

This will build all the code and run all the unit tests.

`./gradle build` creates all the necessary artifacts \(Webapp, Jars and Docker images\) so that you can run Airbyte locally.

## Run in `dev` mode with `docker-compose`

```bash
./gradlew build
docker-compose --env-file .env.dev -f docker-compose.yaml -f docker-compose.dev.yaml up
```

The build will take a few minutes. Once it completes, Airbyte compiled at current git revision will be running in `dev` mode in your environment.

In `dev` mode, all data will be persisted in `/tmp/dev_root`.

## Run acceptance tests

To run acceptance \(end-to-end\) tests, you must have the Airbyte running locally.

```bash
./gradlew build
VERSION=dev docker-compose up
./gradlew :airbyte-tests:acceptanceTests
```

## Develop on individual applications

The easiest way to develop on one of Airbyte's modules is to spin up the whole Airbyte system on your workstation, and shutdown the module you want to work on.

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

### Develop on `airbyte-server` \(APIs\)

* Spin up Airbyte locally.
* Stop the `server`.

```bash
docker-compose stop server
```

* Run the `server` with the command line. It will build and start a `server` with the current state of the code. You can also start the `server` from your IDE if you need to use a debugger.

```bash
./gradlew :airbyte-server:run
```

* Make sure everything is working by testing out a call to the API.

```bash
curl -H "Content-Type: application/json"\
 -X POST localhost:8001/api/v1/workspaces/get\
 -d '{ "workspaceId": "5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6" }'
```

* Happy Hacking!

_Note: We namespace most API calls with a workspace id. For now there is only ever one workspace that is hardcoded to the id used in this example. If you ever need a workspace id, just use this one._

### Develop on `airbyte-scheduler`

* Spin up Airbyte locally.
* Stop the `scheduler`.

```bash
docker-compose stop scheduler
```

* Run the `scheduler` with the command line. It will build and start a `scheduler` with the current state of the code. You can also start the `scheduler`from your IDE if you need to use a debugger.

```bash
./gradlew :airbyte-scheduler:run
```

* Happy Hacking!

### Resetting the Airbyte developer environment

Sometimes you'll want to reset the data in your local environment. One common case for this is if you are updating an connector's entry in the database (`airbyte-config/init/src/main/resources/config`), often the easiest thing to do, is wipe the local database and start it from scratch. To reset your data back to a clean install of Airbyte, follow these steps:

* Delete the datastore volumes in docker
    ```bash
    docker-compose --env-file .env.dev -f docker-compose.yaml -f docker-compose.dev.yaml down -v
    ```
* Remove the data on disk
    ```bash
    rm -rf /tmp/dev_root
    rm -rf /tmp/airbyte_local
    ```
*  Rebuild the project
    ```bash
    ./gradlew build
    docker-compose --env-file .env.dev -f docker-compose.yaml -f docker-compose.dev.yaml up -V
    ```
