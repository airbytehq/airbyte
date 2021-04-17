# Intermediate Concepts
## Checkpointing via batching 
A batch is a group of logically related records used by the framework for checkpointing state (see the state management section [TODO]()). 
When batching is enabled, a state message will be output by the connector after reading every batch. Batching is completely optional and is provided as a way for connectors to checkpoint state in a more granular way than basic interval-based state checkpointing. Batching is typically used when reading a large amount of data or when the underlying data source imposes strict rate limits that make it difficult to re-read the same data over and over again. This being said, interval-based checkpointing is compatible with batching with one difference: intervals are counted within a batch rather than across the entirety of the records. In other words, the counter used to determine if the interval (e.g: every 10k records) has been reached resets at the beginning of every batch.     

The relationship between records in a batch is up to the author of the connector, but batches are typically used to implement date-based checkpointing
for example to group records generated within a particular hour, day, or month etc. 

Batches can be hard-coded or generated dynamically (e.g: by making a query). 

The only restriction imposed on batches is that they must be described with a list of `dict`s returned from the `Stream.batches()` method, where each `dict` describes a batch. The `dict`s may have any schema, and are passed as input to each stream's `read_stream` method. This way, the connector can read the current batch description (the input `dict`) and use that to make queries as needed.

### Use cases
If your use case requires saving state based on an interval e.g: only 10,000 records but nothing more sophisticated, then batching is not necessary and you can instead set the `state_checkpoint_interval` property on a source.

#### The Slack connector: time-based batching for large datasets
Slack is a chat platform for businesses. Collectively, a company can easily post tens or hundreds of thousands of messages in a single 
Slack instance per day. So when writing a connector to pull chats from Slack, it's easy to run into rate limits or for the sync to take a very long 
time to complete because of the large amount of data. So we want to. 

This is a great usecase for batching. The `messages` stream, which outputs one record per chat message, can batch records by time e.g: hourly. 
It implements this by specifying the beginning and end timestamp of each hour that it wants to pull data from. Then after all the records in a given
hour have been read, the connector outputs a STATE message to indicate that state should be checkpointed. This way, if the connector
ever fails during a sync (for example if the API goes down) then at most, it will reread only one hour's worth of messages.   

See the implementation of the Slack connector here [TODO]().
