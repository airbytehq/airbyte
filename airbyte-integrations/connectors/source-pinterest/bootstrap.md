## Core streams

Pinterest is a REST based API. Connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

Connector has such core streams:

- [Account analytics](https://developers.pinterest.com/docs/api/v5/#operation/user_account/analytics) \(Incremental\)
- [Boards](https://developers.pinterest.com/docs/api/v5/#operation/boards/list) \(Full table\)
  - [Board sections](https://developers.pinterest.com/docs/api/v5/#operation/board_sections/list) \(Full table\)
    - [Pins on board section](https://developers.pinterest.com/docs/api/v5/#operation/board_sections/list_pins) \(Full table\)
  - [Pins on board](https://developers.pinterest.com/docs/api/v5/#operation/boards/list_pins) \(Full table\)
- [Ad accounts](https://developers.pinterest.com/docs/api/v5/#operation/ad_accounts/list) \(Full table\)
  - [Ad account analytics](https://developers.pinterest.com/docs/api/v5/#operation/ad_account/analytics) \(Incremental\)
  - [Campaigns](https://developers.pinterest.com/docs/api/v5/#operation/campaigns/list) \(Incremental\)
    - [Campaign analytics](https://developers.pinterest.com/docs/api/v5/#operation/campaigns/list) \(Incremental\)
  - [Ad groups](https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/list) \(Incremental\)
    - [Ad group analytics](https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/analytics) \(Incremental\)
  - [Ads](https://developers.pinterest.com/docs/api/v5/#operation/ads/list) \(Incremental\)
    - [Ad analytics](https://developers.pinterest.com/docs/api/v5/#operation/ads/analytics) \(Incremental\)

Connector uses `start_date` config for initial reports sync depend on connector and current date as an end data.

Connector has `window_in_days` config which allows set the amount of days for each data-chunk begining from start_date. Default: 30 days. Max: 30 days.

See [this](https://docs.airbyte.io/integrations/sources/pinterest) link for the nuances about the connector.
