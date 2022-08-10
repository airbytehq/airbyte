# Salesloft

## Overview

The Salesloft source supports both `Full Refresh` and `Incremental` syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

Several output streams are available from this source. A list of these streams can be found below in the [Streams](salesloft.md#streams) section.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

## Getting started

### Requirements

* Salesloft Account
* Salesloft OAuth credentials

### Setup guide

Getting an admin level oauth credentials require registering as partner. Check out [here](https://salesloft.com/partner-with-salesloft/) and [here](https://help.salesloft.com/s/article/Getting-Started-with-the-Salesloft-API)

## Streams

List of available streams:

* CadenceMemberships
* Cadences
* People
* Users
* Emails
* Account Stages
* Account Tiers
* Accounts
* Actions
* Calls
* Emails Templates
* Emails Template Attachements
* Imports
* Notes
* Person Stages
* Phone Number Assignments
* Steps
* Team Templates
* Team Template Attachements
* CRM Activities
* CRM Users
* Groups
* Successes






## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.3   | 2022-03-28 | [11460](https://github.com/airbytehq/airbyte/pull/11460) | Added multiple new streams (Accounts, Actions, Calls, Notes ... ) |
| 0.1.2   | 2022-03-17 | [11239](https://github.com/airbytehq/airbyte/pull/11239) | Added new Emails stream |
| 0.1.1   | 2022-01-25 | [8617](https://github.com/airbytehq/airbyte/pull/8617) | Update connector fields title/description |
| 0.1.0   | 2021-10-22 | [6962](https://github.com/airbytehq/airbyte/pull/6962) | Salesloft Connector |
