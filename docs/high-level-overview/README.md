---
description: Here is a high level view of Airbyte's components.
---

# Architecture

![3.048-Kilometer view](../.gitbook/assets/10-000-feet-view%20%281%29%20%281%29.png)

* `UI`: Acts as the control center for Airbyte. From the UI, you can configure new integration connections. You can also track the different syncing jobs and view logs.
* `Config Store`: Stores all the connections information \(credentials, frequency...\).
* `Scheduler Store`: Stores statuses and job information for the scheduler bookkeeping.
* `Config API`: Allows the UI to read and update connection information.
* `Scheduler API`: Allows the UI to read and control jobs \(schema discovery, connection testing, logs...\).
* `Scheduler`: The scheduler orchestrates all the data syncing from the source integration to the destination. It is responsible for tracking success/failure and for triggering syncs based on the configured frequency.
* `Worker`: The worker connects to the source system, pulls the data and writes it to the destination system.
* `Temporary Storage`: A storage that workers can use whenever they need to spill data on a disk.

