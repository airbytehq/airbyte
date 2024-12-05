# XKCD

## Prerequisites

XKCD is an open API, so no credentials are needed to set up the source.

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
| 0.2.2   | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version   |
| 0.2.1 | 2024-07-28 | [42834](https://github.com/airbytehq/airbyte/pull/42834) | Fix Metadata sha256 digest |
| 0.2.0 | 2024-07-25 | [42479](https://github.com/airbytehq/airbyte/pull/42479) | Migrate to low code manifest only connector |
| 0.1.10 | 2024-07-20 | [42380](https://github.com/airbytehq/airbyte/pull/42380) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41682](https://github.com/airbytehq/airbyte/pull/41682) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41393](https://github.com/airbytehq/airbyte/pull/41393) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41204](https://github.com/airbytehq/airbyte/pull/41204) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40817](https://github.com/airbytehq/airbyte/pull/40817) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40389](https://github.com/airbytehq/airbyte/pull/40389) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40164](https://github.com/airbytehq/airbyte/pull/40164) | Update dependencies |
| 0.1.3 | 2024-06-06 | [39293](https://github.com/airbytehq/airbyte/pull/39293) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-05-20 | [38401](https://github.com/airbytehq/airbyte/pull/38401) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2022-10-24 | [18386](https://github.com/airbytehq/airbyte/pull/18386) | Readded xkcd to source def yaml |
| 0.1.0 | 2022-10-17 | [18049](https://github.com/airbytehq/airbyte/pull/18049) | Initial version/release of the connector. |

</details>
