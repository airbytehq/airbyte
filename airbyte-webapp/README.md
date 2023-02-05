# airbyte-webapp

This module contains the Airbyte Webapp. It is a React app written in TypeScript. It runs in a Docker container. A very lightweight nginx server runs in that Docker container and serves the webapp.

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### `npm test`

Launches the test runner in the interactive watch mode.<br />

### `npm run build`

Builds the app for production to the `build` folder.<br />

### VERSION=yourtag ./gradlew :airbyte-webapp:assemble

Builds the app and Docker image and tags the image with `yourtag`.
Note: needs to be run from the root directory of the Airbyte project.

### Using a custom version of the CDK declarative manifest schema for the connector builder UI

When working on the connector builder UI and doing changes to the CDK and the webapp at the same time, you can start the dev server with `CDK_MANIFEST_PATH` or `CDK_VERSION` environment variables set to have the correct Typescript types built. If `CDK_VERSION` is set, it's loading the specified version of the CDK from pypi instead of the default one, if `CDK_MANIFEST_PATH` is set, it's copying the schema file locally.

For example:
```
CDK_MANIFEST_PATH=../../airbyte/airbyte-cdk/python/airbyte_cdk/sources/declarative/declarative_componenpnt_schema.yaml npm start
```

## Entrypoints
* `airbyte-webapp/src/App.tsx` is the entrypoint into the OSS version of the webapp.
* `airbyte-webapp/src/packages/cloud/App.tsx` is the entrypoint into the Cloud version of the webapp.
