# XKCD

This page guides you through the process of setting up the xkcd source connector.

## Prerequisites

XKCD is an open API, so no credentials are needed to set up the surce.

## Supported sync modes

The xkcd source connector supports on full sync refresh.

## Supported Streams

That is just one stream for xkcd, that retrieves a given comic metadata.

### Performance considerations

XKCD does not perform rate limiting.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                   |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------- |
| 0.1.4 | 2024-06-22 | [40164](https://github.com/airbytehq/airbyte/pull/40164) | Update dependencies |
| 0.1.3 | 2024-06-06 | [39293](https://github.com/airbytehq/airbyte/pull/39293) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-05-20 | [38401](https://github.com/airbytehq/airbyte/pull/38401) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2022-10-24 | [18386](https://github.com/airbytehq/airbyte/pull/18386) | Readded xkcd to source def yaml |
| 0.1.0 | 2022-10-17 | [18049](https://github.com/airbytehq/airbyte/pull/18049) | Initial version/release of the connector. |

</details>
