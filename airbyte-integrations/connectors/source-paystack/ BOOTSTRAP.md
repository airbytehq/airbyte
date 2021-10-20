# Cart

paystack.com is a straightforward CRUD REST API. Connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

It consists of some REST resources like customers, transactions, transfers, subscriptions, etc. each of which have a list endpoint with a "from" filter that can be used to perform incremental syncs. 

Auth uses an API token which can be found in the Paystack dashboard.
Pagination uses a cursor pagination strategy.

See the links below for information about specific streams and some nuances about the connector:
- [Paystack connector documentation](https://docs.airbyte.io/integrations/sources/paystack)
