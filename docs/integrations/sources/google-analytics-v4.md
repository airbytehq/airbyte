# Google Analytics (Universal Analytics)

Google has discontinued Universal Analytics in favor of Google Analytics 4. Airbyte has archived this connector and the Reporting API v4 is no longer available. Use the [Google Analytics 4 (GA4) connector](https://docs.airbyte.com/integrations/sources/google-analytics-data-api) instead to sync data from Google Analytics 4.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                      |
|:--------| :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------- |
| 0.4.20 | 2025-12-09 | [60624](https://github.com/airbytehq/airbyte/pull/60624) | Update dependencies |
| 0.4.19 | 2025-05-10 | [59771](https://github.com/airbytehq/airbyte/pull/59771) | Update dependencies |
| 0.4.18 | 2025-05-03 | [59242](https://github.com/airbytehq/airbyte/pull/59242) | Update dependencies |
| 0.4.17 | 2025-04-26 | [58782](https://github.com/airbytehq/airbyte/pull/58782) | Update dependencies |
| 0.4.16 | 2025-04-12 | [57685](https://github.com/airbytehq/airbyte/pull/57685) | Update dependencies |
| 0.4.15 | 2025-04-05 | [57055](https://github.com/airbytehq/airbyte/pull/57055) | Update dependencies |
| 0.4.14 | 2025-03-29 | [55945](https://github.com/airbytehq/airbyte/pull/55945) | Update dependencies |
| 0.4.13 | 2025-03-08 | [55305](https://github.com/airbytehq/airbyte/pull/55305) | Update dependencies |
| 0.4.12 | 2025-03-01 | [54944](https://github.com/airbytehq/airbyte/pull/54944) | Update dependencies |
| 0.4.11 | 2025-02-22 | [54405](https://github.com/airbytehq/airbyte/pull/54405) | Update dependencies |
| 0.4.10 | 2025-02-01 | [52803](https://github.com/airbytehq/airbyte/pull/52803) | Update dependencies |
| 0.4.9 | 2025-01-25 | [52318](https://github.com/airbytehq/airbyte/pull/52318) | Update dependencies |
| 0.4.8 | 2025-01-18 | [51687](https://github.com/airbytehq/airbyte/pull/51687) | Update dependencies |
| 0.4.7 | 2025-01-11 | [51120](https://github.com/airbytehq/airbyte/pull/51120) | Update dependencies |
| 0.4.6 | 2025-01-04 | [50921](https://github.com/airbytehq/airbyte/pull/50921) | Update dependencies |
| 0.4.5 | 2024-12-28 | [50589](https://github.com/airbytehq/airbyte/pull/50589) | Update dependencies |
| 0.4.4 | 2024-12-21 | [50063](https://github.com/airbytehq/airbyte/pull/50063) | Update dependencies |
| 0.4.3 | 2024-12-14 | [49507](https://github.com/airbytehq/airbyte/pull/49507) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.4.2 | 2024-11-04 | [48206](https://github.com/airbytehq/airbyte/pull/48206) | Update dependencies |
| 0.4.1 | 2024-10-29 | [47766](https://github.com/airbytehq/airbyte/pull/47766) | Update dependencies |
| 0.4.0 | 2024-07-01 | [40244](https://github.com/airbytehq/airbyte/pull/40244) | Deprecate the connector |
| 0.3.3 | 2024-06-21 | [39940](https://github.com/airbytehq/airbyte/pull/39940) | Update dependencies |
| 0.3.2 | 2024-06-04 | [38934](https://github.com/airbytehq/airbyte/pull/38934) | [autopull] Upgrade base image to v1.2.1 |
| 0.3.1   | 2024-04-19 | [37432](https://github.com/airbytehq/airbyte/pull/36267) | Fix empty response error for test stream                                                     |
| 0.3.0   | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0`                                                              |
| 0.2.5   | 2024-02-09 | [35101](https://github.com/airbytehq/airbyte/pull/35101) | Manage dependencies with Poetry.                                                             |
| 0.2.4   | 2024-01-22 | [34323](https://github.com/airbytehq/airbyte/pull/34323) | Update setup dependencies                                                                    |
| 0.2.3   | 2024-01-18 | [34353](https://github.com/airbytehq/airbyte/pull/34353) | Add End date option                                                                          |
| 0.2.2   | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image              |
| 0.2.1   | 2023-07-11 | [28149](https://github.com/airbytehq/airbyte/pull/28149) | Specify date format to support datepicker in UI                                              |
| 0.2.0   | 2023-06-26 | [27738](https://github.com/airbytehq/airbyte/pull/27738) | License Update: Elv2                                                                         |
| 0.1.36  | 2023-04-13 | [22223](https://github.com/airbytehq/airbyte/pull/22223) | Fix custom report with Segments dimensions                                                   |
| 0.1.35  | 2023-05-31 | [26885](https://github.com/airbytehq/airbyte/pull/26885) | Remove `authSpecification` from spec in favour of `advancedAuth`                             |
| 0.1.34  | 2023-01-27 | [22006](https://github.com/airbytehq/airbyte/pull/22006) | Set `AvailabilityStrategy` for streams explicitly to `None`                                  |
| 0.1.33  | 2022-12-23 | [20858](https://github.com/airbytehq/airbyte/pull/20858) | Fix check connection                                                                         |
| 0.1.32  | 2022-11-04 | [18965](https://github.com/airbytehq/airbyte/pull/18965) | Fix for `discovery` stage, when `custom_reports` are provided with single stream as `dict`   |
| 0.1.31  | 2022-10-30 | [18670](https://github.com/airbytehq/airbyte/pull/18670) | Add `Custom Reports` schema validation on `check connection`                                 |
| 0.1.30  | 2022-10-13 | [17943](https://github.com/airbytehq/airbyte/pull/17943) | Fix pagination                                                                               |
| 0.1.29  | 2022-10-12 | [17905](https://github.com/airbytehq/airbyte/pull/17905) | Handle exceeded daily quota gracefully                                                       |
| 0.1.28  | 2022-09-24 | [16920](https://github.com/airbytehq/airbyte/pull/16920) | Added segments and filters to custom reports                                                 |
| 0.1.27  | 2022-10-07 | [17717](https://github.com/airbytehq/airbyte/pull/17717) | Improve CHECK by using `ga:hits` metric.                                                     |
| 0.1.26  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/15087) | Migrate to per-stream states.                                                                |
| 0.1.25  | 2022-07-27 | [15087](https://github.com/airbytehq/airbyte/pull/15087) | Fix documentationUrl                                                                         |
| 0.1.24  | 2022-07-26 | [15042](https://github.com/airbytehq/airbyte/pull/15042) | Update `additionalProperties` field to true from schemas                                     |
| 0.1.23  | 2022-07-22 | [14949](https://github.com/airbytehq/airbyte/pull/14949) | Add handle request daily quota error                                                         |
| 0.1.22  | 2022-06-30 | [14298](https://github.com/airbytehq/airbyte/pull/14298) | Specify integer type for ga:dateHourMinute dimension                                         |
| 0.1.21  | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                                                             |
| 0.1.20  | 2022-04-28 | [12426](https://github.com/airbytehq/airbyte/pull/12426) | Expose `isDataGOlden` field and always resync data two days back to make sure it is golden   |
| 0.1.19  | 2022-04-19 | [12150](https://github.com/airbytehq/airbyte/pull/12150) | Minor changes to documentation                                                               |
| 0.1.18  | 2022-04-07 | [11803](https://github.com/airbytehq/airbyte/pull/11803) | Improved documentation                                                                       |
| 0.1.17  | 2022-03-31 | [11512](https://github.com/airbytehq/airbyte/pull/11512) | Improved Unit and Acceptance tests coverage, fixed `read` with abnormally large state values |
| 0.1.16  | 2022-01-26 | [9480](https://github.com/airbytehq/airbyte/pull/9480)   | Reintroduce `window_in_days` and log warning when sampling occurs                            |
| 0.1.15  | 2021-12-28 | [9165](https://github.com/airbytehq/airbyte/pull/9165)   | Update titles and descriptions                                                               |
| 0.1.14  | 2021-12-09 | [8656](https://github.com/airbytehq/airbyte/pull/8656)   | Fix date format in schemas                                                                   |
| 0.1.13  | 2021-12-09 | [8676](https://github.com/airbytehq/airbyte/pull/8676)   | Fix `window_in_days` validation issue                                                        |
| 0.1.12  | 2021-12-03 | [8175](https://github.com/airbytehq/airbyte/pull/8175)   | Fix validation of unknown metric(s) or dimension(s) error                                    |
| 0.1.11  | 2021-11-30 | [8264](https://github.com/airbytehq/airbyte/pull/8264)   | Corrected date range                                                                         |
| 0.1.10  | 2021-11-19 | [8087](https://github.com/airbytehq/airbyte/pull/8087)   | Support `start_date` before the account has any data                                         |
| 0.1.9   | 2021-10-27 | [7410](https://github.com/airbytehq/airbyte/pull/7410)   | Add check for correct permission for requested `view_id`                                     |
| 0.1.8   | 2021-10-13 | [7020](https://github.com/airbytehq/airbyte/pull/7020)   | Add intermediary auth config support                                                         |
| 0.1.7   | 2021-10-07 | [6414](https://github.com/airbytehq/airbyte/pull/6414)   | Declare OAuth parameters in Google sources                                                   |
| 0.1.6   | 2021-09-27 | [6459](https://github.com/airbytehq/airbyte/pull/6459)   | Update OAuth Spec File                                                                       |
| 0.1.3   | 2021-09-21 | [6357](https://github.com/airbytehq/airbyte/pull/6357)   | Fix OAuth workflow parameters                                                                |
| 0.1.2   | 2021-09-20 | [6306](https://github.com/airbytehq/airbyte/pull/6306)   | Support of Airbyte OAuth initialization flow                                                 |
| 0.1.1   | 2021-08-25 | [5655](https://github.com/airbytehq/airbyte/pull/5655)   | Corrected validation of empty custom report                                                  |
| 0.1.0   | 2021-08-10 | [5290](https://github.com/airbytehq/airbyte/pull/5290)   | Initial Release                                                                              |

</details>
