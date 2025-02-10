# Pinterest

This page contains the setup guide and reference information for the Pinterest source connector.

## Prerequisites

<!-- env:cloud -->

When setting up the Pinterest source connector with Airbyte Cloud, be aware that Pinterest does not
allow configuring permissions during the OAuth authentication process. Therefore, the following
permissions will be requested during authentication:

- See all of your advertising data, including ads, ad groups, campaigns, etc.
- See your public boards, including group boards you join.
- See your secret boards.
- See all of your catalogs data.
- See your public Pins.
- See your secret Pins.
- See your user accounts and followers.

For more information on the scopes required for Pinterest OAuth, please refer to the
[Pinterest API Scopes documentation](https://developers.pinterest.com/docs/getting-started/scopes/#Read%20scopes).

<!-- /env:cloud -->

<!-- env:oss -->

To set up the Pinterest source connector with Airbyte Open Source, you'll need your Pinterest
[App ID and secret key](https://developers.pinterest.com/docs/getting-started/set-up-app/) and the
[refresh token](https://developers.pinterest.com/docs/getting-started/authentication/#Refreshing%20an%20access%20token).

<!-- /env:oss -->

## Setup guide

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Pinterest** from the Source type dropdown.
4. Enter the name for the Pinterest connector.
5. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date
   will be replicated. If this field is blank, Airbyte will replicate all data. As per Pinterest API
   restriction, the date cannot be more than 90 days in the past.
6. The **OAuth2.0** authorization method is selected by default. Click **Authenticate your Pinterest
   account**. Log in and authorize your Pinterest account.
7. (Optional) Enter a Start Date using the provided date picker, or by manually entering the date in
   YYYY-MM-DD format. Data added on and after this date will be replicated. If no date is set, it
   will default to the latest allowed date by the report API (913 days from today).
8. (Optional) Select one or multiple status values from the dropdown menu. For the ads, ad_groups,
   and campaigns streams, specifying a status will filter out records that do not match the
   specified ones. If a status is not specified, the source will default to records with a status of
   either ACTIVE or PAUSED.
9. (Optional) Add custom reports if needed. For more information, refer to the corresponding
   section.
10. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Pinterest** from the Source type dropdown.
4. Enter the name for the Pinterest connector.
5. For **Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date
   will be replicated. If this field is blank, Airbyte will replicate all data. As per Pinterest API
   restriction, the date cannot be more than 90 days in the past.
6. The **OAuth2.0** authorization method is selected by default. For **Client ID** and **Client
   Secret**, enter your Pinterest
   [App ID and secret key](https://developers.pinterest.com/docs/getting-started/set-up-app/). For
   **Refresh Token**, enter your Pinterest
   [Refresh Token](https://developers.pinterest.com/docs/getting-started/authentication/#Refreshing%20an%20access%20token).
7. (Optional) Enter a Start Date using the provided date picker, or by manually entering the date in
   YYYY-MM-DD format. Data added on and after this date will be replicated. If no date is set, it
   will default to the latest allowed date by the report API (913 days from today).
8. (Optional) Select one or multiple status values from the dropdown menu. For the ads, ad_groups,
   and campaigns streams, specifying a status will filter out records that do not match the
   specified ones. If a status is not specified, the source will default to records with a status of
   either ACTIVE or PAUSED.
9. (Optional) Add custom reports if needed. For more information, refer to the corresponding
   section.
10. Click **Set up source**.
<!-- /env:oss -->

## Supported sync modes

The Pinterest source connector supports the following
[sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Account analytics](https://developers.pinterest.com/docs/api/v5/#operation/user_account/analytics)
  \(Incremental\)
- [Boards](https://developers.pinterest.com/docs/api/v5/#operation/boards/list) \(Full refresh\)
- [Board sections](https://developers.pinterest.com/docs/api/v5/#operation/board_sections/list)
  \(Full refresh\)
- [Pins on board section](https://developers.pinterest.com/docs/api/v5/#operation/board_sections/list_pins)
  \(Full refresh\)
- [Pins on board](https://developers.pinterest.com/docs/api/v5/#operation/boards/list_pins) \(Full
  refresh\)
- [Ad accounts](https://developers.pinterest.com/docs/api/v5/#operation/ad_accounts/list) \(Full
  refresh\)
- [Ad account analytics](https://developers.pinterest.com/docs/api/v5/#operation/ad_account/analytics)
  \(Incremental\)
- [Campaigns](https://developers.pinterest.com/docs/api/v5/#operation/campaigns/list)
  \(Incremental\)
- [Campaign analytics](https://developers.pinterest.com/docs/api/v5/#operation/campaigns/list)
  \(Incremental\)
- [Campaign Analytics Report](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report)
  \(Incremental\)
- [Campaign Targeting Report](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report)
  \(Incremental\)
- [Ad Groups](https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/list)
  \(Incremental\)
- [Ad Group Analytics](https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/analytics)
  \(Incremental\)
- [Ad Group Report](https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/analytics)
  \(Incremental\)
- [Ad Group Targeting Report](https://developers.pinterest.com/docs/api/v5/#operation/ad_groups/analytics)
  \(Incremental\)
- [Ads](https://developers.pinterest.com/docs/api/v5/#operation/ads/list) \(Incremental\)
- [Ad analytics](https://developers.pinterest.com/docs/api/v5/#operation/ads/analytics)
  \(Incremental\)
- [Catalogs](https://developers.pinterest.com/docs/api/v5/#operation/catalogs/list) \(Full refresh\)
- [Catalogs Feeds](https://developers.pinterest.com/docs/api/v5/#operation/feeds/list) \(Full
  refresh\)
- [Catalogs Product Groups](https://developers.pinterest.com/docs/api/v5/#operation/catalogs_product_groups/list)
  \(Full refresh\)
- [Audiences](https://developers.pinterest.com/docs/api/v5/#operation/audiences/list) \(Full
  refresh\)
- [Keywords](https://developers.pinterest.com/docs/api/v5/#operation/keywords/get) \(Full refresh\)
- [Conversion Tags](https://developers.pinterest.com/docs/api/v5/#operation/conversion_tags/list)
  \(Full refresh\)
- [Customer Lists](https://developers.pinterest.com/docs/api/v5/#tag/customer_lists) \(Full
  refresh\)
- [Advertizer Report](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report)
  \(Incremental\)
- [Advertizer Targeting Report](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report)
  \(Incremental\)
- [Pin Promotion Report](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report)
  \(Incremental\)
- [Pin Promotion Targeting Report](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report)
  \(Incremental\)
- [Product Group Report](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report)
  \(Incremental\)
- [Product Group Targeting Report](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report)
  \(Incremental\)
- [Product Item Report](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report)
  \(Incremental\)
- [Keyword Report](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report)
  \(Incremental\)

## Custom reports

Custom reports in the Pinterest connector allow you to create personalized analytics reports for
your account. You can tailor these reports to your specific needs by choosing from various
properties:

1. **Name**: A unique identifier for the report.
2. **Level**: Specifies the data aggregation level, with options like ADVERTISER, CAMPAIGN,
   AD_GROUP, etc. The default level is ADVERTISER.
3. **Granularity**: Determines the data granularity, such as TOTAL, DAY, HOUR, etc. The default is
   TOTAL, where metrics are aggregated over the specified date range.
4. **Columns**: Identifies the data columns to be included in the report.
5. **Click Window Days (Optional)**: The number of days used for conversion attribution from a pin
   click action. This applies to Pinterest Tag conversion metrics. Defaults to 30 days if not
   specified.
6. **Engagement Window Days (Optional)**: The number of days used for conversion attribution from an
   engagement action. Engagements include saves, closeups, link clicks, and carousel card swipes.
   This applies to Pinterest Tag conversion metrics. Defaults to 30 days if not specified.
7. **View Window Days (Optional)**: The number of days used as the conversion attribution window for
   a view action. This applies to Pinterest Tag conversion metrics. Defaults to 1 day if not
   specified.
8. **Conversion Report Time (Optional)**: Indicates the date by which the conversion metrics
   returned will be reported. There are two dates associated with a conversion event: the date of ad
   interaction and the date of conversion event completion. The default is TIME_OF_AD_ACTION.
9. **Attribution Types (Optional)**: Lists the types of attribution for the report, such as
   INDIVIDUAL or HOUSEHOLD.
10. **Start Date (Optional)**: The start date for the report in YYYY-MM-DD format, defaulting to the
    latest allowed date by the report API (913 days from today).

For more detailed information and guidelines on creating custom reports, please refer to the
[Pinterest API documentation](https://developers.pinterest.com/docs/api/v5/#operation/analytics/create_report).

## Performance considerations

The connector is restricted by the Pinterest
[requests limitation](https://developers.pinterest.com/docs/reference/ratelimits/).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.0.29 | 2025-02-01 | [53001](https://github.com/airbytehq/airbyte/pull/53001) | Update dependencies |
| 2.0.28 | 2025-01-25 | [52502](https://github.com/airbytehq/airbyte/pull/52502) | Update dependencies |
| 2.0.27 | 2025-01-11 | [51377](https://github.com/airbytehq/airbyte/pull/51377) | Update dependencies |
| 2.0.26 | 2025-01-04 | [50933](https://github.com/airbytehq/airbyte/pull/50933) | Update dependencies |
| 2.0.25 | 2024-12-28 | [50710](https://github.com/airbytehq/airbyte/pull/50710) | Update dependencies |
| 2.0.24 | 2024-12-21 | [50302](https://github.com/airbytehq/airbyte/pull/50302) | Update dependencies |
| 2.0.23 | 2024-12-14 | [49040](https://github.com/airbytehq/airbyte/pull/49040) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.0.22 | 2024-11-04 | [48280](https://github.com/airbytehq/airbyte/pull/48280) | Update dependencies |
| 2.0.21 | 2024-10-29 | [47074](https://github.com/airbytehq/airbyte/pull/47074) | Update dependencies |
| 2.0.20 | 2024-10-12 | [46815](https://github.com/airbytehq/airbyte/pull/46815) | Update dependencies |
| 2.0.19 | 2024-10-05 | [46482](https://github.com/airbytehq/airbyte/pull/46482) | Update dependencies |
| 2.0.18 | 2024-09-28 | [46104](https://github.com/airbytehq/airbyte/pull/46104) | Update dependencies |
| 2.0.17 | 2024-09-21 | [45838](https://github.com/airbytehq/airbyte/pull/45838) | Update dependencies |
| 2.0.16 | 2024-09-14 | [45566](https://github.com/airbytehq/airbyte/pull/45566) | Update dependencies |
| 2.0.15 | 2024-09-07 | [45283](https://github.com/airbytehq/airbyte/pull/45283) | Update dependencies |
| 2.0.14 | 2024-08-31 | [45060](https://github.com/airbytehq/airbyte/pull/45060) | Update dependencies |
| 2.0.13 | 2024-08-24 | [44752](https://github.com/airbytehq/airbyte/pull/44752) | Update dependencies |
| 2.0.12 | 2024-08-17 | [44346](https://github.com/airbytehq/airbyte/pull/44346) | Update dependencies |
| 2.0.11 | 2024-08-12 | [43838](https://github.com/airbytehq/airbyte/pull/43838) | Update dependencies |
| 2.0.10 | 2024-08-10 | [43642](https://github.com/airbytehq/airbyte/pull/43642) | Update dependencies |
| 2.0.9 | 2024-08-03 | [43280](https://github.com/airbytehq/airbyte/pull/43280) | Update dependencies |
| 2.0.8 | 2024-07-30 | [39559](https://github.com/airbytehq/airbyte/pull/39559) | Ensure config_error when state has improper format and update CDK version |
| 2.0.7 | 2024-07-27 | [42603](https://github.com/airbytehq/airbyte/pull/42603) | Update dependencies |
| 2.0.6 | 2024-07-20 | [42343](https://github.com/airbytehq/airbyte/pull/42343) | Update dependencies |
| 2.0.5 | 2024-07-13 | [41765](https://github.com/airbytehq/airbyte/pull/41765) | Update dependencies |
| 2.0.4 | 2024-07-10 | [41449](https://github.com/airbytehq/airbyte/pull/41449) | Update dependencies |
| 2.0.3 | 2024-07-06 | [39972](https://github.com/airbytehq/airbyte/pull/39972) | Update dependencies |
| 2.0.2 | 2024-06-10 | [39367](https://github.com/airbytehq/airbyte/pull/39367) | Fix type error when start date was not provided |
| 2.0.1 | 2024-06-04 | [39037](https://github.com/airbytehq/airbyte/pull/39037) | [autopull] Upgrade base image to v1.2.1 |
| 2.0.0 | 2024-05-20 | [37698](https://github.com/airbytehq/airbyte/pull/37698) | Migrate to low-code |
| 1.3.3 | 2024-04-24 | [36655](https://github.com/airbytehq/airbyte/pull/36655) | Schema descriptions and CDK 0.80.0 |
| 1.3.2 | 2024-04-08 | [36912](https://github.com/airbytehq/airbyte/pull/36912) | Fix icon |
| 1.3.1 | 2024-04-03 | [36806](https://github.com/airbytehq/airbyte/pull/36806) | Update airbyte-cdk count bug to emit recordCount as float |
| 1.3.0 | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0` |
| 1.2.0 | 2024-02-20 | [35465](https://github.com/airbytehq/airbyte/pull/35465) | Per-error reporting and continue sync on stream failures |
| 1.1.1 | 2024-02-12 | [35159](https://github.com/airbytehq/airbyte/pull/35159) | Manage dependencies with Poetry. |
| 1.1.0 | 2023-11-22 | [32747](https://github.com/airbytehq/airbyte/pull/32747) | Update docs and spec. Add missing `placement_traffic_type` field to AdGroups stream |
| 1.0.0 | 2023-11-16 | [32595](https://github.com/airbytehq/airbyte/pull/32595) | Add airbyte_type: timestamp_without_timezone to date-time fields across all streams. Rename `Advertizer*` streams to `Advertiser*` |
| 0.8.2 | 2023-11-20 | [32672](https://github.com/airbytehq/airbyte/pull/32672) | Fix backoff waiting time |
| 0.8.1 | 2023-11-16 | [32601](https://github.com/airbytehq/airbyte/pull/32601) | added ability to create custom reports |
| 0.8.0 | 2023-11-16 | [32592](https://github.com/airbytehq/airbyte/pull/32592) | Make start_date optional; add suggested streams; add missing fields |
| 0.7.2 | 2023-11-08 | [32299](https://github.com/airbytehq/airbyte/pull/32299) | added default `AvailabilityStrategy`, fixed bug which cases duplicated requests, added new streams: Catalogs, CatalogsFeeds, CatalogsProductGroups, Audiences, Keywords, ConversionTags, CustomerLists, CampaignTargetingReport, AdvertizerReport, AdvertizerTargetingReport, AdGroupReport, AdGroupTargetingReport, PinPromotionReport, PinPromotionTargetingReport, ProductGroupReport, ProductGroupTargetingReport, ProductItemReport, KeywordReport |
| 0.7.1 | 2023-11-01 | [32078](https://github.com/airbytehq/airbyte/pull/32078) | handle non json response |
| 0.7.0 | 2023-10-25 | [31876](https://github.com/airbytehq/airbyte/pull/31876) | Migrated to base image, removed token based authentication mthod becuase access_token is valid for 1 day only |
| 0.6.0 | 2023-07-25 | [28672](https://github.com/airbytehq/airbyte/pull/28672) | Add report stream for `CAMPAIGN` level |
| 0.5.3 | 2023-07-05 | [27964](https://github.com/airbytehq/airbyte/pull/27964) | Add `id` field to `owner` field in `ad_accounts` stream |
| 0.5.2 | 2023-06-02 | [26949](https://github.com/airbytehq/airbyte/pull/26949) | Update `BoardPins` stream with `note` property |
| 0.5.1 | 2023-05-11 | [25984](https://github.com/airbytehq/airbyte/pull/25984) | Add pattern for start_date |
| 0.5.0 | 2023-05-17 | [26188](https://github.com/airbytehq/airbyte/pull/26188) | Add `product_tags` field to the `BoardPins` stream |
| 0.4.0 | 2023-05-16 | [26112](https://github.com/airbytehq/airbyte/pull/26112) | Add `is_standard` field to the `BoardPins` stream |
| 0.3.0 | 2023-05-09 | [25915](https://github.com/airbytehq/airbyte/pull/25915) | Add `creative_type` field to the `BoardPins` stream |
| 0.2.6 | 2023-04-26 | [25548](https://github.com/airbytehq/airbyte/pull/25548) | Fix `format` issue for `boards` stream schema for fields with `date-time` |
| 0.2.5 | 2023-04-19 | [0](https://github.com/airbytehq/airbyte/pull/0) | Update `AMOUNT_OF_DAYS_ALLOWED_FOR_LOOKUP` to 89 days |
| 0.2.4 | 2023-02-25 | [23457](https://github.com/airbytehq/airbyte/pull/23457) | Add missing columns for analytics streams for pinterest source |
| 0.2.3 | 2023-03-01 | [23649](https://github.com/airbytehq/airbyte/pull/23649) | Fix for `HTTP - 400 Bad Request` when requesting data >= 90 days |
| 0.2.2 | 2023-01-27 | [22020](https://github.com/airbytehq/airbyte/pull/22020) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.2.1 | 2022-12-15 | [20532](https://github.com/airbytehq/airbyte/pull/20532) | Bump CDK version |
| 0.2.0 | 2022-12-13 | [20242](https://github.com/airbytehq/airbyte/pull/20242) | Add data-type normalization up to the schemas declared |
| 0.1.9 | 2022-09-06 | [15074](https://github.com/airbytehq/airbyte/pull/15074) | Add filter based on statuses |
| 0.1.8 | 2022-10-21 | [18285](https://github.com/airbytehq/airbyte/pull/18285) | Fix type of `start_date` |
| 0.1.7 | 2022-09-29 | [17387](https://github.com/airbytehq/airbyte/pull/17387) | Set `start_date` dynamically based on API restrictions. |
| 0.1.6 | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Use CDK 0.1.89 |
| 0.1.5 | 2022-09-16 | [16799](https://github.com/airbytehq/airbyte/pull/16799) | Migrate to per-stream state |
| 0.1.4 | 2022-09-06 | [16161](https://github.com/airbytehq/airbyte/pull/16161) | Add ability to handle `429 - Too Many Requests` error with respect to `Max Rate Limit Exceeded Error` |
| 0.1.3 | 2022-09-02 | [16271](https://github.com/airbytehq/airbyte/pull/16271) | Add support of `OAuth2.0` authentication method |
| 0.1.2 | 2021-12-22 | [10223](https://github.com/airbytehq/airbyte/pull/10223) | Fix naming of `AD_ID` and `AD_ACCOUNT_ID` fields |
| 0.1.1 | 2021-12-22 | [9043](https://github.com/airbytehq/airbyte/pull/9043) | Update connector fields title/description |
| 0.1.0 | 2021-10-29 | [7493](https://github.com/airbytehq/airbyte/pull/7493) | Release Pinterest CDK Connector |
</details>
