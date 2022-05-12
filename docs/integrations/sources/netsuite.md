# Netsuite

## Overview
The Netsuite source connects to Netsuite using the new [REST API](https://netsuite.custhelp.com/app/answers/detail/a_id/86949). The source allows for all your custom objects and fields by dynamically pulling the metadata from Netsuite. This does mean it can take a little while to retrieve your configuration in the user interface.

## Setup Guide

### Requirements
Your Netsuite account has to have the REST API and token based authentication enabled. You will also need to [set up an integration, create a token for it](https://netsuite.custhelp.com/app/answers/detail/a_id/86950#subsect_1559218712) and make sure it has permissions to access all of the record types you want to extract.

Ensure the role has `Permissions->Reports->SuireAnalytics Workbook` allowed, or else you will not be able to perform queries.

## Supported Streams
All objects, including custom ones, should be supported, however subobjects have not been set up.

## Changelog
| Version | Date       | Pull Request                                             | Subject                     |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------- |
| 0.1.0   | 2022-05-10 | [11738](https://github.com/airbytehq/airbyte/pull/11738) | The Netsuite Source is created |
