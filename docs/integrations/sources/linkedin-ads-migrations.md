# LinkedIn Ads Migration Guide

## Upgrading to 2.0.0

Version 2.0.0 introduces changes in the primary key selected for all \*-analytics streams (including custom ones) from pivotValues[array of strings] to string_of_pivot_values[string] so that it is compatible with more destination types.

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

Clearing your data is required for the affected streams in order to continue syncing successfully. To clear your data for the affected streams, follow the steps below:

1. Select **Connections** in the main navbar and select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema** to bring in any schema changes. Any detected schema changes will be listed for your review.
   2. Select **OK** to approve changes.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Clear affected streams** option is checked to ensure your streams continue syncing successfully with the new schema.
4. Select **Save connection**.

This will clear the data in your destination for the subset of streams with schema changes. After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).

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

Clearing your data is required for the affected streams in order to continue syncing successfully. To clear your data for the affected streams, follow the steps below:

1. Select **Connections** in the main navbar and select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema** to bring in any schema changes. Any detected schema changes will be listed for your review.
   2. Select **OK** to approve changes.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Clear affected streams** option is checked to ensure your streams continue syncing successfully with the new schema.
4. Select **Save connection**.

This will clear the data in your destination for the subset of streams with schema changes. After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).
