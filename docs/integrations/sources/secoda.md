# Secoda API

## Sync overview

This source can sync data from the [Secoda API](https://docs.secoda.co/secoda-api). At present, this connector only supports full refresh syncs, meaning that each time you use the connector, it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

* collections
* tables
* terms

### Features

| Feature           | Supported?(Yes/No) | Notes |
| :---------------  | :----------------- | :--- |
| Full Refresh Sync | Yes                |      |
| Incremental Sync  | No                 |      |

### Performance considerations

## Getting started

### Requirements

* API Access

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-27 | [#18378](https://github.com/airbytehq/airbyte/pull/18378) | 🎉 New Source: Secoda API [low-code CDK] |

### Configuration

For setting up the Secoda source connector in Airbyte, you need to obtain your Secoda API Key.

1. Go to the [Secoda login page](https://app.secoda.co/signin) and sign in with your credentials.

2. Click on your profile icon in the top right corner of the screen.

3. From the dropdown menu, select "Settings."

4. In the left sidebar of the settings page, click on the "API" tab.

5. Find the "API Keys" section. If you don't have an API key yet, click on the "Create API Key" button.

6. Copy your API Key.

7. Now, you need to input your API Key in the Airbyte Secoda connector configuration form:

   * **Api Key**: Your Secoda API Access Key that you copied in step 6. The key is case sensitive.

The following links may be helpful when setting up the connection:

* Secoda API Key: [Secoda API - Authentication](https://docs.secoda.co/secoda-api/authentication)

After you have provided the required information in the configuration form, click "Test Connection" to ensure that Airbyte can connect successfully to your Secoda API. Once the test is successful, click "Save Changes" to proceed with syncing the data using the Secoda source connector.