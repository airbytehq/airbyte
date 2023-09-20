---
description: >-
  Azure Service Bus provides a queue messaging service.
---

# Azure Service Bus

## Overview

The Airbyte Azure Service Bus destination allows you to send/stream data to a queue in Azure Service Bus.

## Prerequisites

The destination supports Azure SAS authentication only, see [Service Bus connection string](https://learn.microsoft.com/en-us/azure/connectors/connectors-create-api-servicebus?tabs=consumption#get-connection-string).

## Sync overview

### Output schema

Each stream will be output a service bus message with headers. The message headers are

- `_stream`: the name of stream where the data is coming from (also stored as message `Label`)  
- `_namespace`: namespace if available from the stream
- `_stream_keys`: serialized string of the primary key field name(s) (if any)

Additional headers can be set via the `header_map` config key. 

The data will be a serialized JSON, containing the following fields

- `_airbyte_ab_id`: a uuid string assigned to each event.
- `_airbyte_emitted_at`: a long timestamp\(ms\) representing when the event was pulled from the data source.
- `_airbyte_data`: a json string representing source data.

### Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | No                   |       |
| Namespaces                     | Yes                  |       |


### Performance considerations

The maximum size of a non-premium Service Bus queue is 256KB.  

If a source record exceeds the maximum message size at the Service Bus queue, the message will fail.

## Getting started

### Requirements

To use the Service Bus destination, you'll need:

- A Service Bus namespace and queue messaging entity
- A Azure Service Bus Queue to which Airbyte can stream/sync your data
- An Azure Service Bus primary connection string with write privilege

### Setup guide

For each of the above high-level requirements as appropriate, add or point to a follow-along guide. See existing source or destination guides for an example.

For each major cloud provider we support, also add a follow-along guide for setting up Airbyte to connect to that destination. See the Postgres destination guide for an example of what this should look like.

Follow the [seting up Service Bus tutorial step 2](https://learn.microsoft.com/en-us/azure/connectors/connectors-create-api-servicebus?tabs=consumption#step-2-get-connection-authentication-requirements) guide create/access your connection string. 

Once you've successfully configured Service Bus as a destination in Airbyte, delete this connection string from your computer.
