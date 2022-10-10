# Chargebee

Chargebee is the subscription billing and revenue management platform.
It supports two API versions - [V1](https://apidocs.chargebee.com/docs/api/v1?prod_cat_ver=2) and [V2](https://apidocs.chargebee.com/docs/api?prod_cat_ver=2).
It also has two Product Catalog versions - [1.0](https://www.chargebee.com/docs/1.0/product-catalog.html) and [2.0](https://www.chargebee.com/docs/2.0/product-catalog.html).
The streams supported by the connector depend on which catalog version a user's account has. See the [v2 migration guide](https://apidocs.chargebee.com/docs/api/upgrade) for more details.

It uses `chargebee` - a [public client library](https://github.com/chargebee/chargebee-python).

See the links below for information about specific streams and some nuances about the connector:
- [information about streams](https://docs.google.com/spreadsheets/d/1s-MAwI5d3eBlBOD8II_sZM7pw5FmZtAJsx1KJjVRFNU/edit#gid=1796337932) (`Chargebee` tab)
- [nuances about the connector](https://docs.airbyte.io/integrations/sources/chargebee)
