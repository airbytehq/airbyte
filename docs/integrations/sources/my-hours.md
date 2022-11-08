# My Hours

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | No |  |

This source syncs data from the [My Hours API](https://documenter.getpostman.com/view/8879268/TVmV4YYU).

## Supported Tables

This source allows you to synchronize the following data tables:

* Time logs
* Clients
* Projects
* Team members
* Tags

## Getting started

**Requirements**
In order to use the My Hours API you need to provide the credentials to an admin My Hours account.

### Performance Considerations (Airbyte Open-Source)

Depending on the amount of team members and time logs the source provides a property to change the pagination size for the time logs query. Typically a pagination of 30 days is a correct balance between reliability and speed. But if you have a big amount of monthly entries you might want to change this value to a lower value.


## CHANGELOG

| Version | Date       | Pull Request                                           | Subject |
| :------ | :--------- | :----------------------------------------------------- | :------ |
| 0.1.1   | 2022-06-08 | [12964](https://github.com/airbytehq/airbyte/pull/12964) | Update schema for time_logs stream |
| 0.1.0   | 2021-11-26 | [8270](https://github.com/airbytehq/airbyte/pull/8270) | New Source: My Hours |
