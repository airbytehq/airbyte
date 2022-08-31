## Running Cypress tests locally
Except as noted, commands are written as if run from inside the `airbyte-webapp-e2e-tests/` directory.

Prerequisites:
1) install the e2e test dependencies and tooling with `npm install`
2) build the OSS backend for the current commit with `SUB_BUILD=PLATFORM ../gradlew clean build`
3) create the test database: `npm run createdb`
4) start the OSS backend: `VERSION=dev docker-compose --file ../docker-compose.yaml up`

If you want the ability to change the frontend as you test (to add `data-testid` attributes to the components being tested, for example, or to practice test-driven development), there are a few additional steps. These are optional, but recommended:
5) run `docker-compose stop webapp` to turn off the dockerized frontend build (which uses a production-style build instead of a hot-reloading dev server)
6) the following two commands should be run separately, so open another terminal window and `cd` into the `airbyte-webapp/`
7) if you have not already done so, run `npm install` to install the frontend app's dependencies
8) start the frontend development server with `npm start`

Now you're ready to start the test suite! Ensure you're back in the `airbyte-webapp-e2e-tests/` directory, and then
9) start the cypress test runner with `npm run cypress:open`
