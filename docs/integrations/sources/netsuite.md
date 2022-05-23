# Netsuite

## Overview
The Netsuite source connects to Netsuite using the new [REST API](https://netsuite.custhelp.com/app/answers/detail/a_id/86949). The source allows for all your custom record types and fields by dynamically pulling the metadata from Netsuite. This does mean it can take a little while to retrieve your configuration in the user interface.

## Setup Guide

### Requirements
Your Netsuite account has to have the REST API and token based authentication enabled. You will also need to [set up an integration, create a token for it](https://netsuite.custhelp.com/app/answers/detail/a_id/86950#subsect_1559218712) and make sure it has permissions to access all of the record types you want to extract.

Ensure the role has `Permissions -> Reports -> SuireAnalytics Workbook` allowed, or else you will not be able to perform queries.

Also ensure that your integration user's date format is set up to match 2020-01-01 12:00:00 AM.

For some record types, like currency, you will have to enable Rest Record Service (Beta) in `Setup -> Company -> Enable Features -> SuiteCloud`.

## Supported Streams
All record types, including custom ones.

**This is enabled by dynamically pulling all of the record types and schemas from Netsuite, so setting up a connection can take a while because it has to make a large number of requests.**

## Changelog
| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.1.0   | 2022-05-23 | [11738](https://github.com/airbytehq/airbyte/pull/11738) | The Netsuite Source is created |
