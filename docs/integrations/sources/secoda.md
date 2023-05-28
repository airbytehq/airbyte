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

In this guide, we will show you how to set up the Secoda Source connector in Airbyte. To configure the connector, you will need the API access key for your Secoda account. We will go through the steps to obtain the API key, and then configure the connector.

### Obtain API Access Key from Secoda

1. Log in to your Secoda account at [https://app.secoda.co/](https://app.secoda.co/). If you do not have a Secoda account, you can sign up for a new one.

2. Navigate to the [API Access section](https://app.secoda.co/settings/api) within your account settings by clicking on the gear icon in the top-right corner, then selecting `API Access` from the left navigation menu.

3. You will see a list of your existing API keys. If you haven't created any API keys before, the list will be empty. To create a new API key, click on the `+` icon in the top-right corner.

4. Enter a name for your new API key, and optionally, add a description to help you identify it later. Next, click on `Create API Key` to generate the key.

5. You will see the new API key displayed on your screen. Be sure to copy and store your API key securely since you will not be able to access it again after navigating away from this page.

For more information about managing API keys in Secoda, you can refer to the official [API Authentication documentation](https://docs.secoda.co/secoda-api/authentication).

### Configure the Secoda Source connector

Once you have obtained your API access key from Secoda, you are ready to configure the connector in Airbyte.

1. In the Secoda Source connector configuration form, locate the `Api Key` text field.

2. Paste your Secoda API key in the `Api Key` field. Remember that the key is case sensitive, so make sure you enter it exactly as it appears in your Secoda account.

That's it! After entering the API key, you can proceed with setting up the rest of your Airbyte connection.

## Changelog

| Version | Date       | Pull Request                                              | Subject                                    |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------- |
| 0.1.0   | 2022-10-27 | [#18378](https://github.com/airbytehq/airbyte/pull/18378) | 🎉 New Source: Secoda API [low-code CDK] |