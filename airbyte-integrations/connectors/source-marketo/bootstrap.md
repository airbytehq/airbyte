## Core streams

Marketo is a REST based API. Connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

Connector has such core streams, and all of them except Activity_types support full refresh and incremental sync: 
* [Activity\_types](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Activities/getAllActivityTypesUsingGET). 
* [Campaigns](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Campaigns/getCampaignsUsingGET).
* [Lists](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Static_Lists/getListByIdUsingGET). 
* [Programs](https://developers.marketo.com/rest-api/endpoint-reference/asset-endpoint-reference/#!/Programs/browseProgramsUsingGET). 


## Bulk export streams

Connector also has bulk export streams, which support incremental sync.

* [Activities\_X](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Activities/getLeadActivitiesUsingGET).
* [Leads](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Leads/getLeadByIdUsingGET). 

To be able to pull export data you need to generate 3 separate requests. See [Marketo docs](https://developers.marketo.com/rest-api/bulk-extract/bulk-lead-extract/).

* [First](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#/Bulk_Export_Leads/createExportLeadsUsingPOST) - to create a job

* [Second](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#/Bulk_Export_Leads/enqueueExportLeadsUsingPOST) - to enqueue job

* [Third](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Bulk_Export_Leads/getExportLeadsFileUsingGET) - to poll export data

For get status of extracting see [Status](https://developers.marketo.com/rest-api/endpoint-reference/lead-database-endpoint-reference/#!/Bulk_Export_Leads/getExportLeadsStatusUsingGET) - the status is only updated once every 60 seconds. Job timeout - 180 min.

Connector uses `createdAt` and `updatedAt` config for initial reports sync depend on connector and current date as an end data.

Connector has `window_in_days` config which allows set the amount of days for each data-chunk begining from start_date. Default: 30 days. Max: 30 days.

See [this](https://docs.airbyte.io/integrations/sources/marketo) link for the nuances about the connector.
