### Updating an Integration
1. Make your code changes to an integration
1. Bump the version in the `Dockerfile` of the integration (`LABEL io.airbyte.version=0.1.0`)
1. Iterate by building the the `dev` tagged image and running tests:
    ```
    ./gradlew :airbyte-integrations:singer:postgres:source:integrationTest
    ```
1. Build the integration with the semantic version tag locally:
    ```
    ./tools/integrations/manage.sh build airbyte-integrations/singer/postgres/source
    ```
1. Publish the new version to Docker Hub. 

    ```
    ./tools/integrations/manage.sh publish airbyte-integrations/singer/postgres/source
    ```
1. Update the version of the integration in `Integrations.java` so the new version can be used in Airbyte.
1. Merge the PR with you integration updates.
