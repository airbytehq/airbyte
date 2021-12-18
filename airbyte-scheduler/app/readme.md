# airbyte-scheduler:app

This module contains the Scheduler App. The main method can be found in `SchedulerApp.java`. The Scheduler is responsible for:
1. Determining if it is time to schedule a Sync Job for a Connection.
2. Submitting pending Jobs to the Workers.
3. Retrying failing Jobs.
4. Clearing out old Job History (so it does not become a space concern).
