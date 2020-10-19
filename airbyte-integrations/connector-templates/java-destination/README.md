### How to write a destination integration in java.

1. Prepare integration:
    1. Pick the name of the integration eg. bigquery
       ```
       INTEGRATION_NAME=bigquery
       ```
    1. `mkdir -p airbyte-integrations/connectors/$INTEGRATION_NAME`
    1. `cp -r airbyte-integrations/template/java-destination airbyte-integrations/connectors/$INTEGRATION_NAME/destination`
1. Adjust the copied template:
    1. Rename module 
       ```
       mv airbyte-integrations/connectors/$INTEGRATION_NAME/destination/src/main/java/io/airbyte/integrations/destination/template  airbyte-integrations/connectors/$INTEGRATION_NAME/destination/src/main/java/io/airbyte/integrations/destination/$INTEGRATION_NAME
       ``` 
    1. Rename the template class to an appropriate name for your integration. 
        1. e.g. `DestinationTemplate.java` to `BigQueryDestination.java`.
    1. Change the `mainClass` in `gradle.build` to point to the new class.
1. Define a specification for how to connect to the destination. We recommend placing it the resources directory and naming it `spec.json`. As long as the `spec` method that you implement (discussed later) returns json that meets a valid specification, the integration will work.
    1. todo: add step on how to fill out spec, current description here is really incomplete.
1. `BigQueryDestination.java` is where you actually implement your integration. There are instructional comments in there to help you on your way.
1. Update the docker file to know how to find your integration.
1. todo: add step on how to add documentation.
