# LinkedIn Ads Migration Guide

## Upgrading to 5.0.0

With LinkedIn Ads v5.0.0, we modified primary keys for stream(s): `ad_campaign_analytics`, `Custom Ad Analytics Reports`, `account_users`.

This enhances data integrity and improves the efficiency of your syncs. Users with deduping enabled on those streams might have missing data as records would have been collapsed on the wrong primary key. We highly recommend initiating a connection refresh to ensure all the data is available in the destination.

- `ad_campaign_analytics`
- `Custom Ad Analytics Reports`

| Old PK                               | New PK                                                  | 
|:-------------------------------------|:--------------------------------------------------------|
| `[string_of_pivot_values, end_date]` | `[string_of_pivot_values, end_date, sponsoredCampaign]` | 

- `account_users`

| Old PK      | New PK            | 
|:------------|:------------------|
| `[account]` | `[account, user]` | 

## Migration Steps

Clearing your data is required for the affected streams in order to continue syncing successfully. To clear your data 
for the affected streams, follow the steps below:

1. Select **Connections** in the main navbar and select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema** to bring in any schema changes. Any detected schema changes will be listed for your review.
   2. Select **OK** to approve changes.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Clear affected streams** option is checked to ensure your streams continue syncing successfully with the new schema.
4. Select **Save connection**.

This will clear the data in your destination for the subset of streams with schema changes. After the clear succeeds, 
trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/operator-guides/clear).

## Upgrading to 4.0.0

Version 3.X.X introduced a regression in the connector that was reverted in 4.0.0. If you were using 3.X.X, please go through the migration steps. If you were still using 2.X.X, please upgrade to 4.0.0; after that, there are no additional actions required.

## Migration Steps

Clearing your data is required for the affected streams in order to continue syncing successfully. To clear your data 
for the affected streams, follow the steps below:

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
3. Uncheck all streams except the affected ones.
4. Select **Save changes** at the bottom of the page.
5. Select the **Settings** tab.
6. Press the **Clear your data** button.
7. Return to the **Schema** tab.
8. Check all your streams.

This will clear the data in your destination for the subset of streams with schema changes. After the clear succeeds, 
trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, 
see [this page](https://docs.airbyte.com/operator-guides/reset).

## Upgrading to 3.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte. 
As part of our commitment to delivering exceptional service, we are transitioning source-linkedin-ads from 
the Python Connector Development Kit (CDK) to our innovative low-code framework. This is part of a strategic move 
to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts 
on improving the performance and features of our evolving platform and growing catalog. However, due to differences 
between the Python and low-code CDKs, this migration constitutes a breaking change.

## Migration Steps

Clearing your data is required for the affected streams in order to continue syncing successfully. To clear your data 
for the affected streams, follow the steps below:

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
3. Uncheck all streams except the affected ones.
4. Select **Save changes** at the bottom of the page.
5. Select the **Settings** tab.
6. Press the **Clear your data** button.
7. Return to the **Schema** tab.
8. Check all your streams.

This will clear the data in your destination for the subset of streams with schema changes. After the clear succeeds, 
trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, 
see [this page](https://docs.airbyte.com/operator-guides/reset).

## Upgrading to 2.0.0

Version 2.0.0 introduces changes in the primary key selected for all \*-analytics streams (including custom ones) from 
pivotValues[array of strings] to string_of_pivot_values[string] so that it is compatible with more destination types.

- "ad_campaign_analytics"
- "ad_creative_analytics"
- "ad_impression_device_analytics"
- "ad_member_company_size_analytics"
- "ad_member_country_analytics"
- "ad_member_job_function_analytics"
- "ad_member_job_title_analytics"
- "ad_member_industry_analytics"
- "ad_member_seniority_analytics"
- "ad_member_region_analytics"
- "ad_member_company_analytics"

## Migration Steps

Clearing your data is required for the affected streams in order to continue syncing successfully. To clear your data 
for the affected streams, follow the steps below:

1. Select **Connections** in the main navbar and select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema** to bring in any schema changes. Any detected schema changes will be listed for your review.
   2. Select **OK** to approve changes.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Clear affected streams** option is checked to ensure your streams continue syncing successfully with the new schema.
4. Select **Save connection**.

This will clear the data in your destination for the subset of streams with schema changes. After the clear succeeds, 
trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/operator-guides/clear).

## Upgrading to 1.0.0

Version 1.0.0 introduces changes in the primary key selected for all \*-analytics streams (including custom ones).

- "ad_campaign_analytics"
- "ad_creative_analytics"
- "ad_impression_device_analytics"
- "ad_member_company_size_analytics"
- "ad_member_country_analytics"
- "ad_member_job_function_analytics"
- "ad_member_job_title_analytics"
- "ad_member_industry_analytics"
- "ad_member_seniority_analytics"
- "ad_member_region_analytics"
- "ad_member_company_analytics"

## Migration Steps

Clearing your data is required for the affected streams in order to continue syncing successfully. To clear your data 
for the affected streams, follow the steps below:

1. Select **Connections** in the main navbar and select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema** to bring in any schema changes. Any detected schema changes will be listed for your review.
   2. Select **OK** to approve changes.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Clear affected streams** option is checked to ensure your streams continue syncing successfully with the new schema.
4. Select **Save connection**.

This will clear the data in your destination for the subset of streams with schema changes. After the clear succeeds, 
trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/operator-guides/clear).
