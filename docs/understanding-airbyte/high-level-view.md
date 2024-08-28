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
---
%%{init: {"flowchart": {"defaultRenderer": "elk"}} }%%
flowchart LR
    W[fa:fa-display WebApp/UI]
    S[fa:fa-server Config API Server]
    D[(fa:fa-table Config & Jobs)]
    L[(fa:fa-server Launcher)]
    O[(fa:fa-superpowers Orchestrator)]
    Q[(fa:fa-superpowers Queue)]
    T(fa:fa-calendar Temporal/Scheduler)
    W2[1..n Airbyte Workers]
    WL[fa:fa-server Workload API Server]
    
    W -->|sends API requests| S
    S -->|store data| D
    S -->|create workflow| T
    T -->|launch task| W2
    W2 -->|return status| T
    W2 -->|creates job| WL
    WL -->|queues workload| Q
    Q  -->|reads from| L
    L -->|launches| O
    O -->|launches/reads from| Source
    O -->|launches/reads from/writes to| Destination
    O -->|reports status to| WL
```

- **Web App/UI** [`airbyte-webapp`, `airbyte-proxy`]: An easy-to-use graphical interface for interacting with the Airbyte API.
- **Config API Server** [`airbyte-server`, `airbyte-server-api`]: Handles connection between UI and API. Airbyte's main control plane. All operations in Airbyte such as creating sources, destinations, connections, managing configurations, etc.. are configured and invoked from the API.
- **Database Config & Jobs** [`airbyte-db`]: Stores all the connections information \(credentials, frequency...\).
- **Temporal Service** [`airbyte-temporal`]: Manages the task queue and workflows.
- **Worker** [`airbyte-worker`]: The worker connects to a source connector, pulls the data and writes it to a destination.
- **Workload API** [`airbyte-workload-api-server`]: Manages workloads, Airbyte's internal job abstraction.
- **Launcher** [`airbyte-workload-launcher`]: Launches workloads.

The diagram shows the steady-state operation of Airbyte, there are components not described you'll see in your deployment:

- **Cron** [`airbyte-cron`]: Clean the server and sync logs (when using local logs). Regularly updates connector definitions and sweeps old workloads.
- **Bootloader** [`airbyte-bootloader`]: Upgrade and Migrate the Database tables and confirm the enviroment is ready to work.

This is a holistic high-level description of each component. For Airbyte deployed in Kubernetes the structure is very similar with a few changes.
