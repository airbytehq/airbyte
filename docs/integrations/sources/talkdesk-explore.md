# Talkdesk Explore

## Overview

Talkdesk is a software for contact center operations.

The Talkdesk Explore connector uses the [Talkdesk Explore API](https://docs.talkdesk.com/docs/explore-api) to fetch data from usage reports.

### Output schema

The connector supports both Full Refresh and Incremental on the following streams:

* [Calls Report](https://docs.talkdesk.com/docs/calls-report-explore)
* [User Status Report](https://docs.talkdesk.com/docs/user-status-explore)
* [Studio Flow Execution Report](https://docs.talkdesk.com/docs/studio-flow-execution-report)
* [Contacts Report](https://docs.talkdesk.com/docs/contacts-report)
* [Ring Attempts Report](https://docs.talkdesk.com/docs/ring-attempts-report)

### Note on report generation

To request data from one of the endpoints, first you need to generate a report. This is done by a POST request where the payload is the report specifications. Then, the response will be a report ID that you need to use in a GET request to obtain the report's data.

This process is further explained here: [Executing a Report](https://docs.talkdesk.com/docs/executing-report)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Incremental - Dedupe Sync | No |
| SSL connection | Yes |

### Performance considerations

The Explore API has an account-based quota limit of 15 simultaneous reports (executing + enqueued). If this limit is exceeded, the user will receive a 429 (too many requests) response.

## Getting started

### Requirements

* Talkdesk account
* Talkdesk API key (`Client Credentials` auth method)

### Setup guide

Please refer to the [getting started with the API](https://docs.talkdesk.com/docs/api-access) guide.

## Changelog

| Version | Date | Pull Request | Subject |
| 0.1.0 | 2022-02-07 | | New Source: Talkdesk Explore
| :--- | :--- | :--- | :--- |
