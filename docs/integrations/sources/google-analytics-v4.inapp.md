## Prerequisite

* Administrator access to a Google Analytics 4 (GA4) property

## Setup guide

1. Click **Authenticate your account** by selecting Oauth (recommended).
   * If you select Service Account Key Authentication, follow the instructions in our [full documentation](https://docs.airbyte.com/integrations/sources/google-analytics-v4).
2. Log in and Authorize the Google Analytics account.
3. Enter your [Property ID](https://developers.google.com/analytics/devguides/reporting/data/v1/property-id#what_is_my_property_id)
4. Enter the **Start Date** from which to replicate report data in the format YYYY-MM-DD.
5. (Optional) Airbyte generates 8 default reports. To add more reports, you need to add **Custom Reports** as a JSON array describing the custom reports you want to sync from Google Analytics. See below for more information.
6. (Optional) Enter the **Data request time increment in days**. The bigger this value is, the faster the sync will be, but the more likely that sampling will be applied to your data, potentially causing inaccuracies in the returned results. We recommend setting this to 1 unless you have a hard requirement to make the sync faster at the expense of accuracy. The minimum allowed value for this field is 1, and the maximum is 364.

## (Optional) Custom reports

* Custom reports in format `[{"name": "<report-name>", "dimensions": ["<dimension-name>", ...], "metrics": ["<metric-name>", ...]}]`
* Custom report format when using segments and / or filters `[{"name": "<report-name>", "dimensions": ["<dimension-name>", ...], "metrics": ["<metric-name>", ...], "segments":  ["<segment-id-or-dynamic-segment-v3-format]", filter: "<filter-definition-v3-format>"}]`
* When using segments, make sure you add the `ga:segment` dimension.
* Custom reports: [Dimensions and metrics explorer](https://ga-dev-tools.web.app/dimensions-metrics-explorer/)

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Google Analytics 4 (GA4)](https://docs.airbyte.com/integrations/sources/google-analytics-v4).
