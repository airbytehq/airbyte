# CallRail

## Overview

The CailRail source supports Full Refresh and Incremental syncs. 

### Output schema

This Source is capable of syncing the following core Streams:

* [Calls](https://apidocs.callrail.com/#calls)
* [Companies](https://apidocs.callrail.com/#companies)
* [Text Messages](https://apidocs.callrail.com/#text-messages)
* [Users](https://apidocs.callrail.com/#users)


### Features

| Feature | Supported? |
| :--- |:-----------|
| Full Refresh Sync | Yes        |
| Incremental - Append Sync | Yes        |
| Incremental - Dedupe Sync | Yes        |
| SSL connection | No         |
| Namespaces | No         |

## Setup Guide

To configure the CallRail Source connector in Airbyte, you'll need to obtain the required credentials (API Key and Account ID) and set a starting date for fetching data from your CallRail account. Follow the steps below to complete the setup process.

### 1. Obtain API Key

1. Log in to your CallRail account at [https://www.callrail.com/login/](https://www.callrail.com/login/)
2. Click on the **Profile** icon in the top-right corner and select **Account Settings** from the dropdown menu.
3. In the left sidebar, click on **API Keys** under the **Integrations** section.
4. If you already have an API Key, you can copy it from here. If you don't have an API Key, click on **Create API Key**.
5. Enter a description for the API Key, like "Airbyte Connector", and click on **Create API Key**.
6. Copy the generated API Key.

Reference: [CallRail API Key documentation](https://support.callrail.com/hc/en-us/articles/360060401011-API-Keys)

### 2. Obtain Account ID

1. Log in to your CallRail account.
2. Click on the **Profile** icon in the top-right corner and select **Account Settings** from the dropdown menu.
3. Your Account ID is displayed at the top of the **Account Settings** page under the **Account** section. The field is labeled **Account Number**. Note down the Account ID.

Reference: [CallRail Account ID documentation](https://support.callrail.com/hc/en-us/articles/4407430359944-How-do-I-find-my-CallRail-account-number-)

### 3. Set Start Date

The start date parameter is used to specify the date from which to begin fetching data. To set the start date, input a date in the format `YYYY-MM-DD`, e.g., `2020-01-01`.

### 4. Add Credentials and Configure Connector

1. In the Airbyte connector configuration form, enter the API Key and Account ID obtained in the previous steps, and the start date you chose.
2. Run the connector by clicking the **Test Connection** button to verify if the provided credentials are valid and the connection is successful.
3. If the connection test is successful, click on **Save & Continue** to complete the setup process.

Having completed these steps, the CallRail Source connector in Airbyte should now be successfully configured with the necessary credentials and start date. Airbyte will use this information to fetch data from your CallRail account.

## Changelog

| Version | Date       | Pull Request                                            | Subject                           |
| :--- |:-----------|:--------------------------------------------------------|:----------------------------------|
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail                  |