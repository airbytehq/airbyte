# Cart.com

Cart.com is a straightforward CRUD REST API. Connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

It consists of some REST resources like shopping_cart, users, products, etc… each of which have a list endpoint with a timestamp filter that can be used to perform incremental syncs.

Auth uses a pre-created API token which can be created in the UI.
Pagination uses a cursor pagination strategy.
Rate limiting is just a standard exponential backoff when you see a 429 HTTP status code.

See the links below for information about specific streams and some nuances about the connector:

- [information about streams](https://docs.google.com/spreadsheets/d/1s-MAwI5d3eBlBOD8II_sZM7pw5FmZtAJsx1KJjVRFNU/edit#gid=1796337932) (`Cart.com` tab)
- [nuances about the connector](https://docs.airbyte.io/integrations/sources/cart)
