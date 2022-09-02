## Running Cypress tests locally with `cypress open`
The most useful way to run tests locally is with the `cypress open` command. It opens a dispatcher window that lets you select which browser to run (including an Electron child window whose devtools will be very familiar to chrome users) and which tests to run in it. By default, this command is configured to visit page urls from port 3000 (as used by a locally-run dev server), not port 8000 (as used by docker-compose's `webapp` service). If you want to run tests against the dockerized UI instead, leave the `webapp` docker-compose service running in step 4) and start the test runner with `CYPRESS_BASE_URL=http://localhost:8000 npm run cypress:open` in step 8).

Except as noted, all commands are written as if run from inside the `airbyte-webapp-e2e-tests/` directory.

Prerequisites:
1) Install the e2e test dependencies and tooling with `npm install`.
2) Build the OSS backend for the current commit with `SUB_BUILD=PLATFORM ../gradlew clean build`.
3) Create the test database: `npm run createdb`.
4) Start the OSS backend: `VERSION=dev docker-compose --file ../docker-compose.yaml up`. If you want, follow this with `docker-compose stop webapp` to turn off the dockerized frontend build; interactive cypress sessions don't use it.
5) The following two commands will start a separate long-running server, so open another terminal window. In it, `cd` into the `airbyte-webapp/` directory.
6) If you have not already done so, run `npm install` to install the frontend app's dependencies.
7) Start the frontend development server with `npm start`.
8) Back in the `airbyte-webapp-e2e-tests/` directory, start the cypress test runner with `npm run cypress:open`.
