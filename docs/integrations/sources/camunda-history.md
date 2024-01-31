# Camunda History API

<HideInUI>

This page contains the setup guide and reference information for the [Camunda History API](https://camunda.com/platform-7/) source connector.

</HideInUI>

## Overview

The Camunda History API integration allows to pull historical events from Camunda managed workflow.

## Prerequisites

- Camunda History should be enabled

## Setup Guide

### Step 1: Set up Camunda History API

The History Event Stream provides audit information about executed process instances.
[Camunda History API](https://docs.camunda.org/manual/7.20/user-guide/process-engine/history)
History API enabled by default and doesn't require username/password. 

### Step 2: Set up the Camunda History connector in Airbyte

1. Enter BaseUrl for your Camunda engine-rest API endpoint, i.e. http://x.x.x.x:8090/engine-rest 
2. If your Camunda installation has Authentication for API enabled provide Username and Password.(If no authentication required Username and Password can be any values)
3. Enter Start date in a format YYYY-MM-DDTHH:mm:ssZ. This Timestamp will point to the beginning from where you start ingesting Camunda History.
4. Provide batchsize with a number of events pulled in a single rest call. 100 is a good default. Don't set it too high, it might overload the source system.


## Supported sync modes

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |

## Supported streams

It contains several streams corresponding to Camunda History APIs:
  -  batch
  -  decision-instance
  -  task-startedAfter
  -  task-finishedAfter
  -  case-instance-closedAfter
  -  case-instance-createdAfter
  -  process-instance-startedAfter
  -  activity-instance-startedAfter
  -  process-instance-finishedAfter
  -  activity-instance-finishedAfter
  -  case-activity-instance-endedAfter
  -  case-activity-instance-createdAfter

Each record in the stream contains many fields:

The full ist of fileds and their type documented in [Camunda REST](https://docs.camunda.org/manual/7.13/reference/rest/history/)

## joining streams with DBT

Camunda APIs which export events with a start and end time being retrieved by 2 Streams:
API_NAME-startedAfter and API_NAME-finishedAfter or similar

API_NAME-startedAfter - events which have started but haven't yet finished. Such even might not have end date yet.
API_NAME-finishedAfter - events which have finished and have both

We pull both types of events as independent streams so we don't miss any event which havn't finished yet or which has finished after we already recived it with a start only. At the same time it helps avoiding full sync every time so we use cursor. 

Such streams should be merged and de-duped with preference given to completed events.
Example of the [DBT models](https://github.com/metaops-solutions/airbyte-camunda)


## Limitations & Troubleshooting

Depending of the Camunda use some of the streams might be empty. It is best to keep the disabled. 

### Connector limitations

Not all Camunda History APIs are implemented by the connector. Adding them could be quite simple task.

<HideInUI>
## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                             |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------ |
| 0.1.0   | 2024-01-26 | [2942](https://github.com/airbytehq/airbyte/pull/2942)   | Implement Camunda API using the CDK                                                                                |

</HideInUI>