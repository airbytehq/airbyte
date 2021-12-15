The Salesforce API can be used to pull any objects that live in the user’s SF instance. 
There are two types of objects: 

  * **Standard**: Those are the same across all SF instances and have a static schema
  * **Custom**: These are specific to each user’s instance. A user creates a custom object type by creating it in the UI. 
    Think of each custom object like a SQL table with a pre-defined schema. The schema of the object can be discovered through the 
    [Describe](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm) endpoint on the API.
    Then when pulling those objects via API one expect them to conform to the schema declared by the endpoint.

To query an object, one must use [SOQL](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm), Salesforce’s proprietary SQL language. 
An example might be `SELECT * FROM <sobject.name> WHERE SystemModstamp > 2122-01-18T21:18:20.000Z`.

Because the `Salesforce` connector pulls all objects from `Salesforce` dynamically, then all streams are dynamically generated accordingly. 
And at the stage of creating a schema for each stream, we understand whether the stream is dynamic or not (if the stream has one of the 
following fields: `SystemModstamp`, `LastModifiedDate`, `CreatedDate`, `LoginTime`, then it is dynamic). 
Based on this data, for streams that have information about record updates - we filter by `updated at`, and for streams that have information 
only about the date of creation of the record (as in the case of streams that have only the `CreatedDate` field) - we filter by `created at`.
And we assign the Cursor as follows:
```
@property
def cursor_field(self) -> str:
    return self.replication_key
```
`replication_key` is one of the following values: `SystemModstamp`, `LastModifiedDate`, `CreatedDate`, `LoginTime`.

In addition there are two types of APIs exposed by Salesforce:
  * **[REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_queryall.htm)**: completely synchronous
  * **[BULK API](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/queries.htm)**: has larger rate limit allowance (150k objects per day on the standard plan) but is asynchronous and therefore follows a request-poll-wait pattern.
  
See the links below for information about specific streams and some nuances about the connector:
- [information about streams](https://docs.google.com/spreadsheets/d/1s-MAwI5d3eBlBOD8II_sZM7pw5FmZtAJsx1KJjVRFNU/edit#gid=1796337932) (`Salesforce` tab)
- [nuances about the connector](https://docs.airbyte.io/integrations/sources/salesforce)
