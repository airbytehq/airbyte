# Everhour

This page contains the setup guide and reference information for the [Everhour](https://everhour.com/) source connector.

## Prerequisites

- API Key from Everhour. You can follow instructions [here](https://everhour.docs.apiary.io/#) to get one.

## Supported sync modes

Currently, this project only supports full sync mode. 

## Supported Streams

This project supports the following streams:

- Projects Stream
- Tasks Stream
- Time Records Stream
- Clients Stream
- Time Stream
- Users Stream

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                        |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------|
| 0.1.2 | 2024-04-15 | [37155](https://github.com/airbytehq/airbyte/pull/37155) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37155](https://github.com/airbytehq/airbyte/pull/37155) | schema descriptions |
| 0.1.0   | 2023-02-28 | [23593](https://github.com/airbytehq/airbyte/pull/23593)   | Initial Release   |
