### How to write a destination integration in java.
1. Copy the template into a directory with your integration name. `cp -r airbyte-integrations/java-template-destination airbyte-integrations/<name of integration>-destination`.
    1. By convention this should be the name of the target tool with `-destination` appended to it. e.g. `bigquery-destination`. The rest of this tutorial will assume the name: `bigquery-destination`.
1. Adjust the name directory structure to remove `java-template-destination` and `template` and use the integration name instead.
    1. e.g. 
        ```
       mkdir -p airbyte-integrations/bigquery-destination/src/main/java/io/airbyte/integrations/destination/bigquery
       mv airbyte-integrations/bigquery-destination/src/main/java/io/airbyte/integrations/destination/template/DestinationTemplate.java airbyte-integrations/bigquery-destination/src/main/java/io/airbyte/integrations/destination/bigquery/DestinationTemplate.java
       rm -r airbyte-integrations/bigquery-destination/src/main/java/io/airbyte/integrations/destination/template
        ``` 
1. Rename the template class to an appropriate name for your integration. 
    1. e.g. `DestinationTemplate.java` to `BigQueryDestination.java`.
1. Define a specification for how to connect to the destination. We recommend placing it the resources directory and naming it `spec.json`. As long as the `spec` method that you implement (discussed later) returns json that meets a valid specification, the integration will work.
    1. todo: add step on how to fill out spec, current description here is really incomplete.
1. `BigQueryDestination.java` is where you actually implement your integration. There are instructional comments in there to help you on your way.
1. Update the gradle file to know how to build the integration.
    1. e.g. in `airbyte-integrations/java-template-destination/src/main/java/io/airbyte/integrations/destination/bigquery/build.grade`, set the mainClass field to be the fully qualified named of your integration. `mainClass = 'io.airbyte.integrations.destination.bigquery.BigQueryDestination'`
1. Update the docker file to know how to find your integration.
    1. e.g. in `airbyte-integrations/java-template-destination/src/main/java/io/airbyte/integrations/destination/bigquery/dockerfile`, set the `APPLICATION` environment variable to match the top-level directory name of your integration. In the case of `airbyte-integrations/bigquery-destination`, `bigquery-destination` would be the correct value. `ENV APPLICATION bigquery-destination`  
1. todo: add step on how to add documentation.
