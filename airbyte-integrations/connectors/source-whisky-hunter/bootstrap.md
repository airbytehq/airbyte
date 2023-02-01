## Core streams

[Whisky Hunter](https://whiskyhunter.net/api/) is an API. Connector is implemented with the [Airbyte Low-Code CDK](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview).

Connector supports the following three streams:
* `auctions_data`
    * Provides stats about specific auctions.
* `auctions_info`
    * Provides information and metadata about recurring and one-off auctions.
* `distilleries_info`
    * Provides information about distilleries.

Rate Limiting:
* No published rate limit.

Authentication and Permissions:
* No authentication.


See [this](https://docs.airbyte.io/integrations/sources/whisky-hunter) link for the connector docs.
