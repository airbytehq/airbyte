# Plausible

## Requirements

- [Plausible account](https://plausible.io/)
- Plausible [API key](https://plausible.io/docs/stats-api)

## Supported sync modes

| Feature           | Supported?\(Yes/No\) | Notes                                                                                          |
| :---------------- | :------------------- | :--------------------------------------------------------------------------------------------- |
| Full Refresh Sync | Yes                  | [Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite) |
| Incremental Sync  | No                   |                                                                                                |

## Supported Streams

- [Stats - Time Series](https://plausible.io/docs/stats-api#get-apiv1statstimeseries)

### Notes

Plausible is a privacy-first analytics service, and the data available from its API is intentionally 1) less granular and 2) less comprehensive than those available from Google Analytics. As such:

1. when retrieving multi-day data, [metrics](https://plausible.io/docs/stats-api#metrics) are aggregated to a daily grain; and
2. [non-metric properties](https://plausible.io/docs/stats-api#properties) (e.g., referrer, entry page, exit page) cannot be directly exported, only [grouped on](https://plausible.io/docs/stats-api#get-apiv1statsbreakdown).

Thus, this source connector retrieves [all possible metrics](https://plausible.io/docs/stats-api#metrics) on a daily grain, for all days with nonzero website activity.

## Performance Considerations

The [stated rate limit](https://plausible.io/docs/stats-api) is 600 requests per hour per API key, with higher capacities potentially available [upon request](https://plausible.io/contact).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
|:--------|:-----------| :------------------------------------------------------- | :------------- |
| 0.1.3 | 2024-06-04 | [38974](https://github.com/airbytehq/airbyte/pull/38974) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.2 | 2024-05-28 | [38660](https://github.com/airbytehq/airbyte/pull/38660) | Make connector compatible with Builder |
| 0.1.1 | 2024-05-21 | [38494](https://github.com/airbytehq/airbyte/pull/38494) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-30 | [18657](https://github.com/airbytehq/airbyte/pull/18657) | Initial commit |

</details>
