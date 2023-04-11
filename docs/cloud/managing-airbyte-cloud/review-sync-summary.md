# Review the sync summary
The sync summary displays information about synced data, such as the amount of data moved, the number of records read and committed, and the total sync time. Reviewing this summary can help you monitor the sync performance and identify any potential issues.  
 
To review the sync summary:
1. On the [Airbyte Cloud](http://cloud.airbyte.com/) dashboard, click **Connections**.   

2. Click a connection in the list to view its sync history.

    Sync History displays the sync status or [reset](https://docs.airbyte.com/operator-guides/reset/) status (Succeeded, Partial Success, Failed, Cancelled, or Running) and the [sync summary](#sync-summary).  

    :::note 
    
    Airbyte will try to sync your data three times. After a third failure, it will stop attempting to sync.
    
    :::
    
3. To view the full sync log, click the sync summary dropdown.
 
## Sync summary

| Data                            | Description                                                                                                                                             |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| x GB (also measured in KB, MB) | Amount of data moved during the sync. If basic normalization is on, the amount of data would not change since normalization occurs in the destination.  |
| x emitted records              | Number of records read from the source during the sync.                                                                                                 |
| x committed records            | Number of records the destination confirmed it received.                                                                                                |
| xh xm xs                   | Total time (hours, minutes, seconds) for the sync and basic normalization, if enabled, to complete.                                                     | 

:::note

In a successful sync, the number of emitted records and committed records should be the same.

::: 
