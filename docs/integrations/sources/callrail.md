# CallRail

This guide will walk you through setting up the CallRail Source connector in Airbyte. 

## Overview

The CallRail source connector supports Full Refresh and Incremental syncs.

### Output schema

This Source is capable of syncing the following core Streams:

* [Calls](https://apidocs.callrail.com/#calls)
* [Companies](https://apidocs.callrail.com/#companies)
* [Text Messages](https://apidocs.callrail.com/#text-messages)
* [Users](https://apidocs.callrail.com/#users)

## Getting Started

### Requirements

Make sure you have the following requirements before proceeding:

* A CallRail account
* A CallRail API Token

### Obtaining Your API Key and Account ID

1. Log in to your CallRail account.
2. Navigate to your account settings by clicking on the profile picture in the top right corner.
3. Click on "API" in the left sidebar menu.
4. Scroll down to the "API Keys" section and click on "Create a new key".
5. Give your key a name and select the permissions you want to grant it.
6. Click "Create". You will now see your API key displayed on the screen.
7. Copy the value of your API key.

To obtain your Account ID:

1. Navigate to your main CallRail dashboard.
2. Look for the last few digits of the URL in your browser. They should look something like this: `callrail.com/dashboard/1234567/overview`. The digits in this example, `1234567`, are your Account ID.

### Configuring CallRail in Airbyte

1. Open Airbyte in your web browser and sign in to your account.
2. Click on "Create Connection".
3. Select "CallRail" from the dropdown menu.
4. In the "Configuration" section, provide your CallRail API Key, Account ID, and Start Date.
   - For API Key, paste the API key value you copied earlier.
   - For Account ID, type in or paste the last few digits of your CallRail account URL.
   - For Start Date, enter the date in the format `yyyy-mm-dd` from which you want to start syncing data.
5. When you're done, click "Check Connection" to ensure that your configuration is correct.
6. Save your configuration by clicking "Create Connector".
7. Your CallRail connector is now set up and ready to use.

## Changelog

| Version | Date       | Pull Request                                            | Subject                           |
| :--- |:-----------|:--------------------------------------------------------|:----------------------------------|
| 0.1.0 | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail                  |

**Note:** Do not touch anything in this section, or it will break the system.

## Features

| Feature | Supported? |
| :--- |:-----------|
| Full Refresh Sync | Yes        |
| Incremental - Append Sync | Yes        |
| Incremental - Dedupe Sync | Yes        |
| SSL connection | No         |
| Namespaces | No         |