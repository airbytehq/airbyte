# Secoda API

This document outlines how to set up the Secoda API source connector in Airbyte.

## Sync overview

This source can sync data from the [Secoda API](https://docs.secoda.co/secoda-api). At present, this connector only supports full refresh syncs meaning that each time you use the connector, it will sync all available records from scratch. Please use it cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* collections
* tables
* terms

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No | |

## Getting started

### Requirements

* API Access

To get started with the Secoda API source connector in Airbyte, you will need access to your Secoda API key. Please follow these steps to obtain your API key:

1. Log in to your Secoda account.
2. Navigate to the **API Access** page in the left-hand menu.
3. Click on the **Generate New Key** button to create a new API key.
4. Copy the API key and securely save it for use in configuring the Airbyte Secoda API connection.

### Configuration

With your Secoda API key in hand, you can configure the Airbyte Secoda API connection as follows:

1. In the Airbyte connector configuration screen, enter your Secoda API key in the **Api Key** field. 
2. Click **Test Connection** to ensure the connection is successful.
3. Click **Save** to save your configuration.

Please note that the configuration screen is driven by the spec of the Airbyte Connector, which can be found in the following location: [Secoda Connector Spec](https://docs.airbyte.io/integrations/sources/secoda). Ensure that all required fields are filled out correctly, and consult any relevant documentation as necessary.

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-27 | [#18378](https://github.com/airbytehq/airbyte/pull/18378) | 🎉 New Source: Secoda API [low-code CDK] |