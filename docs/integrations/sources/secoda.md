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

## Setup Guide

This guide will walk you through setting up the secoda source connector in Airbyte. To configure this connector, you will need an API Access Key from secoda. Follow the steps below to obtain the required API key and configure the connector.

### Obtaining the API Access Key

1. Log into your secoda account on the [secoda web interface](https://www.secoda.co/login). If you don't have an account, sign up for a free trial or register for an account.
2. After logging in, go to the [API Access](https://my.secoda.co/#/api) section within your account settings.
3. Find the "API Access Key" section. If you haven't already generated a key, click on the "Generate API Key" button.
4. Copy the generated API Key. You'll need to provide this in the Airbyte connector configuration.

**Note:** You can always return to this page to find your API Key if needed.

### Configuring the secoda Connector

Once you have your API Access Key, follow the steps below to configure the secoda source connector in Airbyte.

1. In the connector configuration form, enter the API Access Key you previously obtained from secoda.
   ```
   Api Key: <your-api-key>
   ```
   Make sure to replace `<your-api-key>` with the API key you copied from your secoda account.

2. Click "Check connection" to ensure Airbyte can authenticate and connect to the secoda API using the provided API key.

3. Once the connection is successful, you can continue configuring the rest of the connector settings as needed, such as syncing frequency and any additional options.

You have now successfully set up the secoda source connector in Airbyte. For more information on using the secoda API, visit the [secoda API documentation](https://docs.secoda.co/secoda-api/).

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-27 | [#18378](https://github.com/airbytehq/airbyte/pull/18378) | 🎉 New Source: Secoda API [low-code CDK] |