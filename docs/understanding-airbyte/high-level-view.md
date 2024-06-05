---
description: A high level view of Airbyte's components.
---

# Architecture overview

Airbyte is conceptually composed of two parts: platform and connectors.

The platform provides all the horizontal services required to configure and run data movement operations e.g: the UI, configuration API, job scheduling, logging, alerting, etc. and is structured as a set of microservices.

Connectors are independent modules which push/pull data to/from sources and destinations. Connectors are built in accordance with the [Airbyte Specification](./airbyte-protocol.md), which describes the interface with which data can be moved between a source and a destination using Airbyte. Connectors are packaged as Docker images, which allows total flexibility over the technologies used to implement them.

A more concrete diagram can be seen below:

```mermaid
---
title: Architecture Overview
config:
  theme: neutral
---
flowchart LR
    W[fa:fa-display WebApp/UI]
    S[fa:fa-server Server/Config API]
    D[(fa:fa-table Config & Jobs)]
    T(fa:fa-calendar Temporal)
    W2[1..n Airbyte Workers]
    W -->|sends API requests| S
    S -->|store data| D
    S -->|create workflow| T
    T -->|launch task| W2
    W2 -->|return job| T
    W2 -->|launches| Source
    W2 -->|launches| Destination
```

- **Web App/UI** [`airbyte-webapp`, `airbyte-proxy`]: An easy-to-use graphical interface for interacting with the Airbyte API.
- **Server/Config API** [`airbyte-server`, `airbyte-server-api`]: Handles connection between UI and API. Airbyte's main control plane. All operations in Airbyte such as creating sources, destinations, connections, managing configurations, etc.. are configured and invoked from the API.
- **Database Config & Jobs** [`airbyte-db`]: Stores all the connections information \(credentials, frequency...\).
- **Temporal Service** [`airbyte-temporal`]: Manages the task queue and workflows.
- **Worker** [`airbyte-worker`]: The worker connects to a source connector, pulls the data and writes it to a destination.

The diagram shows the steady-state operation of Airbyte, there are components not described you'll see in your deployment:

- **Cron** [`airbyte-cron`]: Clean the server and sync logs (when using local logs)
- **Bootloader** [`airbyte-bootloader`]: Upgrade and Migrate the Database tables and confirm the enviroment is ready to work.

This is a holistic high-level description of each component. For Airbyte deployed in Kubernetes the structure is very similar with a few changes.
