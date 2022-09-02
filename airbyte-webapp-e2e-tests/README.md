## Running an interactive Cypress session with `npm run cypress:open`
The most useful way to run tests locally is with the `cypress open` command. It opens a dispatcher window that lets you select which tests and browser to run; the Electron browser (whose devtools will be very familiar to chrome users) opens a child window, and having both cypress windows grouped behaves nicely when switching between applications. In an interactive session, you can use `it.skip` and `it.only` to focus on the tests you care about; any change to the source file of a running test will cause tests to be automatically rerun. At the end of a test run, the web page is left "dangling" with all state present at the end of the last test; you can click around, "inspect element", and interact with the page however you wish, which makes it easy to incrementally develop tests.

By default, this command is configured to visit page urls from port 3000 (as used by a locally-run dev server), not port 8000 (as used by docker-compose's `webapp` service). If you want to run tests against the dockerized UI instead, leave the `webapp` docker-compose service running in step 4) and start the test runner with `CYPRESS_BASE_URL=http://localhost:8000 npm run cypress:open` in step 8).

Except as noted, all commands are written as if run from inside the `airbyte-webapp-e2e-tests/` directory.

Steps:
1) If you have not already done so, run `npm install` to install the e2e test dependencies.
2) Build the OSS backend for the current commit with `SUB_BUILD=PLATFORM ../gradlew clean build`.
3) Create the test database: `npm run createdb`.
4) Start the OSS backend: `VERSION=dev docker-compose --file ../docker-compose.yaml up`. If you want, follow this with `docker-compose stop webapp` to turn off the dockerized frontend build; interactive cypress sessions don't use it.
5) The following two commands will start a separate long-running server, so open another terminal window. In it, `cd` into the `airbyte-webapp/` directory.
6) If you have not already done so, run `npm install` to install the frontend app's dependencies.
7) Start the frontend development server with `npm start`.
8) Back in the `airbyte-webapp-e2e-tests/` directory, start the cypress test runner with `npm run cypress:open`.

## Reproducing CI test results with `npm run cypress:ci` or `npm run cypress:ci:record`
Unlike `npm run cypress:open`, `npm run cypress:ci` and `npm run cypress:ci:record` use the dockerized UI (i.e. they expect the UI at port 8000, rather than port 3000). If the OSS backend is running but you have run `docker-compose stop webapp`, you'll have to re-enable it with `docker-compose start webapp`. These trigger headless runs: you won't have a live browser to interact with, just terminal output.

Except as noted, all commands are written as if run from inside the `airbyte-webapp-e2e-tests/` directory.

Steps:
1) If you have not already done so, run `npm install` to install the e2e test dependencies.
2) Build the OSS backend for the current commit with `SUB_BUILD=PLATFORM ../gradlew clean build`.
3) Create the test database: `npm run createdb`.
4) Start the OSS backend: `VERSION=dev docker-compose --file ../docker-compose.yaml up`.
5) Start the cypress test run with `npm run cypress:ci` or `npm run cypress:ci:record`.
