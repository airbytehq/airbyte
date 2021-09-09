The Salesforce API can be used to pull any objects that live in the user’s SF instance. 
There are two types of objects: 

  * **Standard**: Those are the same across all SF instances and have a static schema
  * **Custom**: These are specific to each user’s instance. A user creates a custom object type by creating it in the UI. 
    Think of each custom object like a SQL table with a pre-defined schema. The schema of the object can be discovered through the 
    [Describe](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm) endpoint on the API.
    Then when pulling those objects via API one expect them to conform to the schema declared by the endpoint.

To query an object, one must use [SOQL](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm), Salesforce’s proprietary SQL language. 
An example might be `SELECT * FROM <sobject.name> WHERE SystemModstamp > 2122-01-18T21:18:20.000Z`.

In addition there are two types of APIs exposed by Salesforce:
  * **[REST API](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_queryall.htm)**: completely synchronous
  * **[BULK API](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/queries.htm)**: has larger rate limit allowance (150k objects per day on the standard plan) but is asynchronous and therefore follows a request-poll-wait pattern.
