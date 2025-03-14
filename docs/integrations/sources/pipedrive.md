# Pipedrive

This page contains the setup guide and reference information for the Pipedrive connector.

## Prerequisites

- A Pipedrive account;
- An `API token`;
- A `client_id`, `client_secret`, and `refresh_token`.

## Setup guide

The Pipedrive connector accepts two authentication flows:

### Via API Token Authentication

Step 1 - Enable API Token:

If you don't see API next to the `Your companies` section, it's due to the permission sets handled by the company's admin. The company's admin can give you access to your API token by enabling it for you from the Settings in Pipedrive web app.

For more information, access [enabling API for company users](https://pipedrive.readme.io/docs/enabling-api-for-company-users).

Step 2 - Find the API Token:

You can get the API Token manually from the Pipedrive web app by going to account name (on the top right) > Company settings > Personal preferences > API.

See [How to find the API Token](https://pipedrive.readme.io/docs/how-to-find-the-api-token) for detailed information.

### Via OAuth

Step 1 - Register a Pipedrive app:

Pipedrive allows integrations with its API through **registered apps**. So, to authenticate Airbyte, first you need to create a Pipedrive private app in the marketplace. Follow these [instructions](https://pipedrive.readme.io/docs/marketplace-registering-the-app) to register your integration.

Step 2 - Follow the Oauth Authorization flow:

With the registered app, you can follow the authorization flow to obtain the `client_id`, `client_secret`, and `refresh_token` secrets. Pipedrive has documentation about it: https://pipedrive.readme.io/docs/marketplace-oauth-authorization.

Step 3 - Configure Airbyte:

Now you can fill the fields Client ID, Client Secret, and Refresh Token. Your Pipedrive connector is set up to work with the OAuth authentication.

## Supported sync modes

The Pipedrive connector supports the following sync modes:

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

Apart from `Fields` streams, all other streams support incremental.

- [Activities](https://developers.pipedrive.com/docs/api/v1/Activities#getActivities)

- [ActivityFields](https://developers.pipedrive.com/docs/api/v1/ActivityFields#getActivityFields)

- [ActivityTypes](https://developers.pipedrive.com/docs/api/v1/ActivityTypes#getActivityTypes)

- [Currencies](https://developers.pipedrive.com/docs/api/v1/Currencies#getCurrencies)

- [DealFields](https://developers.pipedrive.com/docs/api/v1/DealFields#getDealFields)

- [DealProducts](https://developers.pipedrive.com/docs/api/v1/Deals#getDealProducts)

- [Deals](https://developers.pipedrive.com/docs/api/v1/Deals#getDeals)

- [Files](https://developers.pipedrive.com/docs/api/v1/Files#getFiles)

- [Filters](https://developers.pipedrive.com/docs/api/v1/Filters#getFilters)

- [Goals](https://developers.pipedrive.com/docs/api/v1/Goals#getGoals)

- [LeadLabels](https://developers.pipedrive.com/docs/api/v1/LeadLabels#getLeadLabels)

- [Leads](https://developers.pipedrive.com/docs/api/v1/Leads#getLeads)

- [Notes](https://developers.pipedrive.com/docs/api/v1/Notes#getNotes)

- [OrganizationFields](https://developers.pipedrive.com/docs/api/v1/OrganizationFields#getOrganizationFields)

- [Organizations](https://developers.pipedrive.com/docs/api/v1/Organizations#getOrganizations)

- [PermissionSets](https://developers.pipedrive.com/docs/api/v1/PermissionSets#getPermissionSets)

- [PersonFields](https://developers.pipedrive.com/docs/api/v1/PersonFields#getPersonFields)

- [Persons](https://developers.pipedrive.com/docs/api/v1/Persons#getPersons)

- [Pipelines](https://developers.pipedrive.com/docs/api/v1/Pipelines#getPipelines)

- [ProductFields](https://developers.pipedrive.com/docs/api/v1/ProductFields#getProductFields)

- [Products](https://developers.pipedrive.com/docs/api/v1/Products#getProducts)

- [Roles](https://developers.pipedrive.com/docs/api/v1/Roles#getRoles)

- [Stages](https://developers.pipedrive.com/docs/api/v1/Stages#getStages)

- [Users](https://developers.pipedrive.com/docs/api/v1/Users#getUsers)

## Performance considerations

The Pipedrive connector will gracefully handle rate limits. For more information, see [the Pipedrive docs for rate limitations](https://pipedrive.readme.io/docs/core-api-concepts-rate-limiting).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2.4.0 | 2025-02-28 | [54716](https://github.com/airbytehq/airbyte/pull/54716) | Refactor: Optimize Parameters, remove redundant code and Improve Manifest Readability |
| 2.3.8 | 2025-02-22 | [47292](https://github.com/airbytehq/airbyte/pull/47292) | Migrate to manifest only format |
| 2.3.7 | 2025-02-08 | [53488](https://github.com/airbytehq/airbyte/pull/53488) | Update dependencies |
| 2.3.6 | 2025-02-01 | [52986](https://github.com/airbytehq/airbyte/pull/52986) | Update dependencies |
| 2.3.5 | 2025-01-25 | [52477](https://github.com/airbytehq/airbyte/pull/52477) | Update dependencies |
| 2.3.4 | 2025-01-18 | [51922](https://github.com/airbytehq/airbyte/pull/51922) | Update dependencies |
| 2.3.3 | 2025-01-11 | [51305](https://github.com/airbytehq/airbyte/pull/51305) | Update dependencies |
| 2.3.2 | 2025-01-04 | [50929](https://github.com/airbytehq/airbyte/pull/50929) | Update dependencies |
| 2.3.1 | 2024-12-28 | [50288](https://github.com/airbytehq/airbyte/pull/50288) | Update dependencies |
| 2.3.0 | 2024-12-17 | [48615](https://github.com/airbytehq/airbyte/pull/48615) | Update airbyte-cdk to use concurrency |
| 2.2.28 | 2024-12-14 | [49692](https://github.com/airbytehq/airbyte/pull/49692) | Update dependencies |
| 2.2.27 | 2024-12-12 | [49041](https://github.com/airbytehq/airbyte/pull/49041) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.2.26 | 2024-11-04 | [48293](https://github.com/airbytehq/airbyte/pull/48293) | Update dependencies |
| 2.2.25 | 2024-10-29 | [47743](https://github.com/airbytehq/airbyte/pull/47743) | Update dependencies |
| 2.2.24 | 2024-10-28 | [47103](https://github.com/airbytehq/airbyte/pull/47103) | Update dependencies |
| 2.2.23 | 2024-10-12 | [46822](https://github.com/airbytehq/airbyte/pull/46822) | Update dependencies |
| 2.2.22 | 2024-10-05 | [46487](https://github.com/airbytehq/airbyte/pull/46487) | Update dependencies |
| 2.2.21 | 2024-09-28 | [46132](https://github.com/airbytehq/airbyte/pull/46132) | Update dependencies |
| 2.2.20 | 2024-09-21 | [45748](https://github.com/airbytehq/airbyte/pull/45748) | Update dependencies |
| 2.2.19 | 2024-09-14 | [45556](https://github.com/airbytehq/airbyte/pull/45556) | Update dependencies |
| 2.2.18 | 2024-09-07 | [45303](https://github.com/airbytehq/airbyte/pull/45303) | Update dependencies |
| 2.2.17 | 2024-08-31 | [44981](https://github.com/airbytehq/airbyte/pull/44981) | Update dependencies |
| 2.2.16 | 2024-08-24 | [44644](https://github.com/airbytehq/airbyte/pull/44644) | Update dependencies |
| 2.2.15 | 2024-08-17 | [44316](https://github.com/airbytehq/airbyte/pull/44316) | Update dependencies |
| 2.2.14 | 2024-08-12 | [43888](https://github.com/airbytehq/airbyte/pull/43888) | Update dependencies |
| 2.2.13 | 2024-08-10 | [43679](https://github.com/airbytehq/airbyte/pull/43679) | Update dependencies |
| 2.2.12 | 2024-08-03 | [43056](https://github.com/airbytehq/airbyte/pull/43056) | Update dependencies |
| 2.2.11 | 2024-07-27 | [42287](https://github.com/airbytehq/airbyte/pull/42287) | Update dependencies |
| 2.2.10 | 2024-07-13 | [41729](https://github.com/airbytehq/airbyte/pull/41729) | Update dependencies |
| 2.2.9 | 2024-07-10 | [41465](https://github.com/airbytehq/airbyte/pull/41465) | Update dependencies |
| 2.2.8 | 2024-07-09 | [41082](https://github.com/airbytehq/airbyte/pull/41082) | Update dependencies |
| 2.2.7 | 2024-07-06 | [40778](https://github.com/airbytehq/airbyte/pull/40778) | Update dependencies |
| 2.2.6 | 2024-06-25 | [40501](https://github.com/airbytehq/airbyte/pull/40501) | Update dependencies |
| 2.2.5 | 2024-06-22 | [40171](https://github.com/airbytehq/airbyte/pull/40171) | Update dependencies |
| 2.2.4 | 2024-06-04 | [39095](https://github.com/airbytehq/airbyte/pull/39095) | [autopull] Upgrade base image to v1.2.1 |
| 2.2.3 | 2024-05-20 | [38405](https://github.com/airbytehq/airbyte/pull/38405) | [autopull] base image + poetry + up_to_date |
| 2.2.2 | 2024-01-11 | [34153](https://github.com/airbytehq/airbyte/pull/34153) | prepare for airbyte-lib |
| 2.2.1 | 2023-11-06 | [31147](https://github.com/airbytehq/airbyte/pull/31147) | Bugfix: handle records with a null data field |
| 2.2.0 | 2023-10-25 | [31707](https://github.com/airbytehq/airbyte/pull/31707) | Add new stream mail |
| 2.1.0 | 2023-10-10 | [31184](https://github.com/airbytehq/airbyte/pull/31184) | Add new stream goals |
| 2.0.1 | 2023-10-13 | [31151](https://github.com/airbytehq/airbyte/pull/31151) | Add additionalProperties in schemas to read custom fields |
| 2.0.0 | 2023-08-09 | [29293](https://github.com/airbytehq/airbyte/pull/29293) | Migrated to Low-Code CDK |
| 1.0.0 | 2023-06-29 | [27832](https://github.com/airbytehq/airbyte/pull/27832) | Remove `followers_count` field from `Products` stream |
| 0.1.19 | 2023-07-05 | [27967](https://github.com/airbytehq/airbyte/pull/27967) | Update `OrganizationFields` and `ProductFields` with `display_field` field |
| 0.1.18 | 2023-06-02 | [26892](https://github.com/airbytehq/airbyte/pull/26892) | Update `DialFields` schema with `pipeline_ids` property |
| 0.1.17 | 2023-03-21 | [24282](https://github.com/airbytehq/airbyte/pull/24282) | Bugfix handle missed `cursor_field` |
| 0.1.16 | 2023-03-08 | [23789](https://github.com/airbytehq/airbyte/pull/23789) | Add 11 new streams |
| 0.1.15 | 2023-03-02 | [23705](https://github.com/airbytehq/airbyte/pull/23705) | Disable OAuth |
| 0.1.14 | 2023-03-01 | [23539](https://github.com/airbytehq/airbyte/pull/23539) | Fix schema for "activities", "check" works if empty "deals" |
| 0.1.13 | 2022-09-16 | [16799](https://github.com/airbytehq/airbyte/pull/16799) | Migrate to per-stream state |
| 0.1.12 | 2022-05-12 | [12806](https://github.com/airbytehq/airbyte/pull/12806) | Remove date-time format from schemas |
| 0.1.10 | 2022-04-26 | [11870](https://github.com/airbytehq/airbyte/pull/11870) | Add 3 streams: DealFields, OrganizationFields and PersonFields |
| 0.1.9 | 2021-12-07 | [8582](https://github.com/airbytehq/airbyte/pull/8582) | Update connector fields title/description |
| 0.1.8 | 2021-11-16 | [7875](https://github.com/airbytehq/airbyte/pull/7875) | Extend schema for "persons" stream |
| 0.1.7 | 2021-11-15 | [7968](https://github.com/airbytehq/airbyte/pull/7968) | Update oAuth flow config |
| 0.1.6 | 2021-10-05 | [6821](https://github.com/airbytehq/airbyte/pull/6821) | Add OAuth support |
| 0.1.5 | 2021-09-27 | [6441](https://github.com/airbytehq/airbyte/pull/6441) | Fix normalization error |
| 0.1.4 | 2021-08-26 | [5943](https://github.com/airbytehq/airbyte/pull/5943) | Add organizations stream |
| 0.1.3 | 2021-08-26 | [5642](https://github.com/airbytehq/airbyte/pull/5642) | Remove date-time from deals stream |
| 0.1.2 | 2021-07-23 | [4912](https://github.com/airbytehq/airbyte/pull/4912) | Update money type to support floating point |
| 0.1.1 | 2021-07-19 | [4686](https://github.com/airbytehq/airbyte/pull/4686) | Update spec.json |
| 0.1.0 | 2021-07-19 | [4686](https://github.com/airbytehq/airbyte/pull/4686) | 🎉 New source: Pipedrive connector |
