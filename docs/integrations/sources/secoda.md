# Secoda API

## Sync Overview

This source can sync data from the [Secoda API](https://docs.secoda.co/secoda-api). At present this connector only supports full refresh syncs, meaning that each time you use the connector, it will sync all available records from scratch. Please use it cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* collections
* tables
* terms

## Getting Started

Follow the steps below to set up the Secoda API source connector in Airbyte.

### Requirements

* API Access

### Configuration

1. In the **Create a new connection** screen, select **Secoda API** in the **Source** field.

2. In the **API Key** field, enter your [Secoda API Access Key](https://docs.secoda.co/secoda-api/authentication). Note that the key is case-sensitive.

3. Leave all other fields as default.

   ```json
   {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Secoda Spec",
    "type": "object",
    "required": [
        "api_key"
    ],
    "additionalProperties": true,
    "properties": {
        "api_key": {
            "title": "Api Key",
            "type": "string",
            "description": "Your API Access Key. See <a href=\"https://docs.secoda.co/secoda-api/authentication\">here</a>. The key is case sensitive.",
            "airbyte_secret": true
        }
    }
   }
   ```

4. Click **Test** to verify the connection to the source.

5. Click **Create** to save the connection configuration.

   You have successfully set up the Secoda API source connector in Airbyte!