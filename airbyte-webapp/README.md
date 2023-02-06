# airbyte-webapp

This module contains the Airbyte Webapp. It is a React app written in TypeScript.
The webapp compiles to static HTML, JavaScript and CSS, which is served (in OSS) via
a nginx in the airbyte-webapp docker image. This nginx also serves as the reverse proxy
for accessing the server APIs in other images.

## Building the webapp

You can build the webapp using Gradle in the root of the repository:

```sh
# Only compile and build the docker webapp image:
SUB_BUILD=PLATFORM ./gradlew :airbyte-webapp:assemble
# Build the webapp and additional artifacts and run tests:
SUB_BUILD=PLATFORM ./gradlew :airbyte-webapp:build
```

## Developing the webapp

For an instruction how to develop on the webapp, please refer to our [documentation](https://docs.airbyte.com/contributing-to-airbyte/developing-locally/#develop-on-airbyte-webapp).

### Entrypoints

* `airbyte-webapp/src/App.tsx` is the entrypoint into the OSS version of the webapp.
* `airbyte-webapp/src/packages/cloud/App.tsx` is the entrypoint into the Cloud version of the webapp.
