# Druid

## Overview

This connector supports read access to the Apache Druid database (https://druid.apache.org/). The connector uses the Apache Calcite based JDBC adapter (https://calcite.apache.org/docs/druid_adapter.html). Since this is built on top of JDBC layer in Airbyte, it supports both full and incremental syncs.

## Requirements

This connector has been tested on a druid installation without user credentials but should work with credentials as well. The model file needed bt the adapter is defined at https://calcite.apache.org/docs/druid_adapter.html. This minimal model file works well. Just copy it into the appropriate field in the source page on airbyte. Change the url's based on your install.
```
{
  "version": "1.0",
  "defaultSchema": "ecom",
  "schemas": [
    {
      "type": "custom",
      "name": "ecom",
      "factory": "org.apache.calcite.adapter.druid.DruidSchemaFactory",
      "operand": {
        "url": "http://localhost:8082",
        "coordinatorUrl": "http://localhost:8081"
      }
    }
  ]
}
```
## Data type

Druid stores the \_\_time column in its own specific format. That is converted to BIGINT while pulling data from Druid.
