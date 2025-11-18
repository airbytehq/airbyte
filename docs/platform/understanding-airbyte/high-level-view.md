---
description: A high level view of Airbyte's components.
---

# Architecture overview

Airbyte is conceptually composed of two parts: platform and connectors.

The platform provides all the horizontal services required to configure and run data movement operations e.g: the UI, configuration API, job scheduling, logging, alerting, etc. and is structured as a set of microservices.

Connectors are independent modules which push/pull data to/from sources and destinations. Connectors are built in accordance with the [Airbyte Specification](./airbyte-protocol.md), which describes the interface with which data can be moved between a source and a destination using Airbyte. Connectors are packaged as Docker images, which allows total flexibility over the technologies used to implement them.

## Data Transfer Modes

Airbyte supports two data transfer modes that are automatically selected based on connector capabilities:

- **Socket Mode**: Records flow directly from source to destination via Unix domain sockets, enabling high-throughput parallel data transfer. A lightweight bookkeeper process handles control messages, state, and logs.
- **Legacy Mode**: Records flow through an orchestrator middleware that sits between source and destination, using standard input/output streams.

Socket mode is used when both source and destination connectors support it, providing significantly higher performance for data movement operations.

### Data Flow Comparison

```mermaid
---
title: Data Transfer Modes
---
flowchart LR
    subgraph Legacy["Legacy Mode"]
        SRC1[Source] --> ORCH[Orchestrator] --> DEST1[Destination]
    end
    
    subgraph Socket["Socket Mode"]
        SRC2[Source] -.->|control| BK[Bookkeeper]
        SRC2 ==>|records via sockets| DEST2[Destination]
        DEST2 -.->|state| BK
    end
```

## Platform Architecture

A more concrete diagram of the platform orchestration can be seen below:

```mermaid
---
title: Architecture Overview
---
%%{init: {"flowchart": {"defaultRenderer": "elk"}} }%%
flowchart LR
    S[fa:fa-server Config API Server]
    D[(fa:fa-table Config & Jobs)]
    L[(fa:fa-server Launcher)]
    OP[(fa:fa-superpowers Operation pod)]
    Q[(fa:fa-superpowers Queue)]
    T(fa:fa-calendar Temporal/Scheduler)
    W2[1..n Airbyte Workers]
    WL[fa:fa-server Workload API Server]
    
    S -->|store data| D
    S -->|create workflow| T
    T -->|launch task| W2
    W2 -->|return status| T
    W2 -->|creates job| WL
    WL -->|queues workload| Q
    Q  -->|reads from| L
    L -->|launches| OP
    O -->|reports status to| WL
```

- **Config API Server** [`airbyte-server`, `airbyte-server-api`]: Airbyte's main controller and graphical user interface. All operations in Airbyte such as creating sources, destinations, connections, managing configurations, etc. are configured and invoked from the API.
- **Database Config & Jobs** [`airbyte-db`]: Stores all the configuration \(credentials, frequency...\) and job history.
- **Temporal Service** [`airbyte-temporal`]: Manages the scheduling and sequencing task queues and workflows.
- **Worker** [`airbyte-worker`]: Reads from the task queues and executes the connection scheduling and sequencing logic, making calls to the workload API.
- **Workload API** [`airbyte-workload-api-server`]: The HTTP interface for enqueuing workloads — the discrete pods that run the connector operations.
- **Launcher** [`airbyte-workload-launcher`]: Consumes events from the workload API and interfaces with k8s to launch workloads.

### Data Transfer Middleware

Within connector operation pods, Airbyte runs middleware containers to process connector output:

- **Bookkeeper** [`airbyte-bookkeeper`]: Used in socket mode. Processes control messages, state, and logs while records flow directly between connectors via sockets.
- **Container Orchestrator** [`airbyte-container-orchestrator`]: Used in legacy mode. Sits between source and destination connectors, processing all data and control messages.

The diagram shows the steady-state operation of Airbyte, there are components not described you'll see in your deployment:

- **Cron** [`airbyte-cron`]: Clean the server and sync logs (when using local logs). Regularly updates connector definitions and sweeps old workloads ensuring eventual consenus.
- **Bootloader** [`airbyte-bootloader`]: Upgrade and Migrate the Database tables and confirm the environment is ready to work.

This is a holistic high-level description of each component. For Airbyte deployed in Kubernetes the structure is very similar with a few changes.
