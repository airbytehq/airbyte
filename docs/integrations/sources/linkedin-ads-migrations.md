# LinkedIn Ads Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 introduces changes in primary key for all *-analytics streams (including custom ones).
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

### Refresh affected schemas and reset data

1. Select **Connections** in the main nav bar.
    1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
    1. Select **Refresh source schema**.
    2. Select **OK**.
:::note
Any detected schema changes will be listed for your review.
:::
3. Select **Save changes** at the bottom of the page.
    1. Ensure the **Reset affected streams** option is checked.
:::note
Depending on destination type you may not be prompted to reset your data.
:::
4. Select **Save connection**. 
:::note
This will reset the data in your destination and initiate a fresh sync.
:::

For more information on resetting your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).
