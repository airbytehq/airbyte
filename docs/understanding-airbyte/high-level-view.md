---
description: A high level view of Airbyte's components.
---

# High-level View

![3.048-Kilometer view](../.gitbook/assets/understanding_airbyte_high_level_architecture.png)

* `UI`: An easy-to-use graphical interface for interacting with the Airbyte API.
* `WebApp Server`: Handles connection between UI and API.
* `Config Store`: Stores all the connections information \(credentials, frequency...\).
* `Scheduler Store`: Stores statuses and job information for the scheduler bookkeeping.
* `Config API`: Airbyte's main control plane. All operations in Airbyte such as creating sources, destinations, connections, managing configurations, etc.. are configured and invoked from the API.
* `Scheduler`: The scheduler takes work requests from the API and sends them to the Temporal service to parallelize. It is responsible for tracking success/failure and for triggering syncs based on the configured frequency.
* `Temporal Service`: Manages the task queue and workflows for the Scheduler. 
* `Worker`: The worker connects to a source, pulls the data and writes it to a destination.
* `Temporary Storage`: A storage that workers can use whenever they need to spill data on a disk.

