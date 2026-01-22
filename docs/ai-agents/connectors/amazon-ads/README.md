# Amazon-Ads agent connector

Amazon Ads is Amazon's advertising platform that enables sellers and vendors to promote their
products across Amazon's marketplace. This connector provides access to advertising profiles
for managing and analyzing advertising campaigns across different marketplaces.


## Example questions

The Amazon-Ads connector is optimized to handle prompts like these.

- List all my advertising profiles across marketplaces
- Show me the profiles for my seller accounts
- What marketplaces do I have advertising profiles in?
- List all portfolios for a specific profile
- Show me all sponsored product campaigns
- What campaigns are currently enabled?
- Find campaigns with a specific targeting type

## Unsupported questions

The Amazon-Ads connector isn't currently able to handle prompts like these.

- Create a new advertising campaign
- Update my campaign budget
- Delete an ad group
- Generate a performance report

## Installation

```bash
uv pip install airbyte-agent-amazon-ads
```

## Usage

```python
from airbyte_agent_amazon_ads import AmazonAdsConnector, AmazonAdsAuthConfig

connector = AmazonAdsConnector(
  auth_config=AmazonAdsAuthConfig(
    client_id="...",
    client_secret="...",
    refresh_token="..."
  )
)
result = await connector.profiles.list()
```


## Full documentation

This connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Profiles | [List](./REFERENCE.md#profiles-list), [Get](./REFERENCE.md#profiles-get) |
| Portfolios | [List](./REFERENCE.md#portfolios-list), [Get](./REFERENCE.md#portfolios-get) |
| Sponsored Product Campaigns | [List](./REFERENCE.md#sponsored-product-campaigns-list), [Get](./REFERENCE.md#sponsored-product-campaigns-get) |


For detailed documentation on available actions and parameters, see this connector's [full reference documentation](./REFERENCE.md).

For the service's official API docs, see the [Amazon-Ads API reference](https://advertising.amazon.com/API/docs/en-us).

## Version information

- **Package version:** 0.1.1
- **Connector version:** 1.0.1
- **Generated with Connector SDK commit SHA:** c713ec4833c2b52dc89926ec68caa343423884cd