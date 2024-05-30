# Amazon Ads Migration Guide

## Upgrading to 5.0.0

The following streams have updated schemas due to a change with the Amazon Ads API:

- `SponsoredBrandsCampaigns`
- `SponsoredBrandsAdGroups`
- `SponsoredProductsCampaigns`
- `SponsoredProductsAdGroupBidRecommendations`

### Schema Changes - Removed/Added Fields

| Stream Name                                  | Removed Fields                                                                                                               | Added Fields                                                                                |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `SponsoredBrandsCampaigns`                   | `serviceStatus`, `bidOptimization`, `bidMultiplier`, `adFormat`, `bidAdjustments`, `creative`, `landingPage`, `supplySource` | `ruleBasedBudget`, `bidding`, `productLocation`, `costType`, `smartDefault`, `extendedData` |
| `SponsoredBrandsAdGroups`                    | `bid`, `keywordId`, `keywordText`, `nativeLanuageKeyword`, `matchType`                                                       | `extendedData`                                                                              |
| `SponsoredProductsCampaigns`                 | `campaignType`, `dailyBudget`, `ruleBasedBudget`, `premiumBidAdjustment`, `networks`                                         | `dynamicBidding`, `budget`, `extendedData`                                                  |
| `SponsoredProductsAdGroupBidRecommendations` | `suggestedBid`                                                                                                               | `theme`, `bidRecommendationsForTargetingExpressions`                                        |

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

```note
Any detected schema changes will be listed for your review.
```

3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.

```note
Depending on destination type you may not be prompted to reset your data.
```

4. Select **Save connection**.

```note
This will reset the data in your destination and initiate a fresh sync.
```

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).

## Upgrading to 4.0.0

Streams `SponsoredBrandsAdGroups` and `SponsoredBrandsKeywords` now have updated schemas.

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

```note
Any detected schema changes will be listed for your review.
```

3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.

```note
Depending on destination type you may not be prompted to reset your data.
```

4. Select **Save connection**.

```note
This will reset the data in your destination and initiate a fresh sync.
```

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).

## Upgrading to 3.0.0

A major update of attribution report stream schemas.
For a smooth migration, a data reset and a schema refresh are needed.
