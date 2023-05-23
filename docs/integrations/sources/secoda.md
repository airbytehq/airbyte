# Secoda API

## Sync overview

This source can sync data from the [Secoda API](https://docs.secoda.co/secoda-api). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* collections
* tables
* terms

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

### Performance considerations

## Getting started

### Requirements

To set up the Secoda source, you will need: 

* An API access key

If you do not already have an API key, follow these steps to obtain one:

1. Log in to Secoda and navigate to the API settings page [here](https://app.secoda.co/api).
2. Click on the "New API Key" button to generate a new API key. This will be displayed on the screen.
3. Make a note of the API key for use in Airbyte.

### Set up in Airbyte

1. In Airbyte, navigate to the page for creating a new connection.
2. In the Source field, select Secoda from the dropdown menu.
3. In the "API Key" field, enter your Secoda API key.
4. Ensure that you have read and agree to the terms and conditions of the Secoda API by checking the box provided.
5. Click "Test" to ensure that you have entered your API key correctly and to check that Airbyte is able to establish a connection to the Secoda API.
6. If the test is successful, click "Create" to create your new connection.

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-27 | [#18378](https://github.com/airbytehq/airbyte/pull/18378) | 🎉 New Source: Secoda API [low-code CDK] |

#### Airbyte Connector Spec

documentationUrl: https://docs.airbyte.com/integrations/sources/secoda

connectionSpecification:

  $schema: http://json-schema.org/draft-07/schema#

  title: Secoda Spec

  type: object

  required:

    - api_key

  additionalProperties: true

  properties:

    api_key:

      title: Api Key

      type: string

      description: >-

        Your API Access Key. See <a

        href="https://docs.secoda.co/secoda-api/authentication">here</a>. The key is

        case sensitive.

      airbyte_secret: true