# Review the sync summary
The job history displays information about synced data, such as the amount of data moved, the number of records read and committed, and the total sync time. Reviewing this summary can help you monitor the sync performance and identify any potential issues.  
 
To review the job history: :
1. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections**.   

2. Click a connection in the list to view its sync history.

    Sync History displays the sync status or [reset](https://docs.airbyte.com/operator-guides/reset/) status. The sync status is defined as: 

    - Succeeded: 100% of the data has been extracted and loaded to the destination
    - Partially Succeeded: a subset of the data has been loaded to the destination
    - Failed: none of the data has been loaded to the destination
    - Cancelled: the sync was cancelled manually before finishing
    - Running: the sync is currently running
    
    ::: note

    In the event of a failure, Airbyte will make several attempts to sync your data before waiting for the next sync to retry. The latest rules can be read about [here](../../understanding-airbyte/jobs.md#retry-rules).

    ::: 
3. To view the full sync log, click the three grey dots next to any sync job. Select "View logs" to open the logs in the browser. 

4. To find a link to the job, click the three grey dots next to any sync job. Select "Copy link to job" to copy the link to your clipboard.

5. To download a copy of the logs locally, click the three grey dots next to any sync job. Select "Donwload logs".
 
## Sync summary

| Data                            | Description                                                                                                                                             |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| x GB (also measured in KB, MB) | Amount of data moved during the sync.  |
| x extracted records              | Number of records read from the source during the sync.                                                                                                 |
| x loaded records            | Number of records the destination confirmed it received.                                                                                                |
| xh xm xs                   | Total time (hours, minutes, seconds) for the sync and basic normalization, if enabled, to complete.                                                     | 


