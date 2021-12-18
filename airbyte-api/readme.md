# airbyte-api

Defines the OpenApi configuration for the Airbyte Configuration API. It also is responsible for generating the following from the API spec:
* Java API client
* Java API server - this generated code is used in `airbyte-server` to allow us to implement the Configuration API in a type safe way. See `ConfigurationApi.java` in `airbyte-server`
* API docs
