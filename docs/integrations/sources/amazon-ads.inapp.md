## Prerequisites

- An [Amazon user](https://www.amazon.com) with access to an [Amazon Ads account](https://advertising.amazon.com)

## Setup Guide

1. Click `Authenticate your Amazon Ads account`. Log in and authorize access to the Amazon account.
2. Select **Region** to pull data from **North America (NA)**, **Europe (EU)**, **Far East (FE)**. See [Amazon Ads documentation](https://advertising.amazon.com/API/docs/en-us/info/api-overview#api-endpoints) for more details.
3. (Optional) **Start Date** can be used to generate reports starting from the specified start date in the format YYYY-MM-DD. The date should not be more than 60 days in the past. If not specified, today's date is used. The date is treated in the timezone of the processed profile.
4. (Optional) **Profile ID(s)** you want to fetch data for. A profile is an advertiser's account in a specific marketplace. See [Amazon Ads docs](https://advertising.amazon.com/API/docs/en-us/concepts/authorization/profiles) for more details. If not specified, data from all Profiles will be synced.
5. (Optional) **State Filter** Filter for Display, Product, and Brand Campaign streams with a state of enabled, paused, or archived. If not specified, all streams regardless of state will be synced.
6. (Optional) **Look Back Window** The amount of days to go back in time to get the updated data from Amazon Ads. After the first sync, data from this date will be synced. 
7. (Optional) **Report Record Types** Optional configuration which accepts an array of string of record types. Leave blank for default behaviour to pull all report types. Use this config option only if you want to pull specific report type(s). See [Amazon Ads docs](https://advertising.amazon.com/API/docs/en-us/reporting/v2/report-types) for more details
9. Click `Set up source`.

### Report Timezones

All the reports are generated relative to the target profile' timezone.

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Amazon Ads](https://docs.airbyte.com/integrations/sources/amazon-ads).
