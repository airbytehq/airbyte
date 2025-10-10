# DataGen

Airbyte's certified DataGen connector offers the following features:

This source generates fake data for testing destinations in speed mode.
Currently supported DataGen type(s): 
- Incremental: Has one column 'id' that contains monotonically increasing integers.
- All Types: Produces one column per Airbyte data type.

## Changelog

<details>
    <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                            |
|:--------|:-----------|:---------------------------------------------------------|:-----------------------------------|
| 0.1.0   | 2025-09-16 | [66331](https://github.com/airbytehq/airbyte/pull/66331) | Creation of initial DataGen Source |
| 0.1.1   | 2025-10-08 | [67110](https://github.com/airbytehq/airbyte/pull/67110) | Addition of proto types            |
</details>
