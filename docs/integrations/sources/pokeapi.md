# PokéAPI

## Tutorials

The PokéAPI is primarly used as a tutorial and educational resource, as it requires zero dependencies. Learn how Airbyte and this connector works with these tutorials:

- [Airbyte Quickstart: An Introduction to Deploying and Syncing](../../using-airbyte/getting-started/readme.md)
- [Airbyte CDK Speedrun: A Quick Primer on Building Source Connectors](../../connector-development/tutorials/cdk-speedrun.md)
- [How to Build ETL Sources in Under 30 Minutes: A Video Tutorial](https://www.youtube.com/watch?v=kJ3hLoNfz_E&t=13s&ab_channel=Airbyte)

## Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental - Append Sync     | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | No         |
| Namespaces                    | No         |

This source uses the fully open [PokéAPI](https://pokeapi.co/docs/v2#info) to serve and retrieve information about Pokémon. This connector should be primarily used for educational purposes or for getting a trial source up and running without needing any dependencies. As this API is fully open and is not rate-limited, no authentication or rate-limiting is performed, so you can use this connector right out of the box without any further configuration.

## Output Schema

Currently, only one output stream is available from this source, which is the Pokémon output stream. This schema is defined [here](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-pokeapi/source_pokeapi/schemas/pokemon.json).

## Rate Limiting & Performance Considerations \(Airbyte Open Source\)

According to the API's [fair use policy](https://pokeapi.co/docs/v2#fairuse), please make sure to cache resources retrieved from the PokéAPI wherever possible. That said, the PokéAPI does not perform rate limiting.

## Data Type Mapping

The PokéAPI uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                         |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------- |
| 0.3.11 | 2025-02-08 | [53472](https://github.com/airbytehq/airbyte/pull/53472) | Update dependencies |
| 0.3.10 | 2025-02-01 | [52980](https://github.com/airbytehq/airbyte/pull/52980) | Update dependencies |
| 0.3.9 | 2025-01-25 | [51878](https://github.com/airbytehq/airbyte/pull/51878) | Update dependencies |
| 0.3.8 | 2025-01-11 | [51308](https://github.com/airbytehq/airbyte/pull/51308) | Update dependencies |
| 0.3.7 | 2024-12-28 | [50708](https://github.com/airbytehq/airbyte/pull/50708) | Update dependencies |
| 0.3.6 | 2024-12-21 | [50261](https://github.com/airbytehq/airbyte/pull/50261) | Update dependencies |
| 0.3.5 | 2024-12-14 | [49689](https://github.com/airbytehq/airbyte/pull/49689) | Update dependencies |
| 0.3.4 | 2024-12-12 | [49337](https://github.com/airbytehq/airbyte/pull/49337) | Update dependencies |
| 0.3.3 | 2024-12-09 | [48220](https://github.com/airbytehq/airbyte/pull/48220) | Update dependencies |
| 0.3.2 | 2024-10-29 | [47927](https://github.com/airbytehq/airbyte/pull/47927) | Update dependencies |
| 0.3.1 | 2024-10-28 | [47461](https://github.com/airbytehq/airbyte/pull/47461) | Update dependencies |
| 0.3.0 | 2024-08-26 | [44791](https://github.com/airbytehq/airbyte/pull/44791) | Refactor connector to manifest-only format |
| 0.2.15 | 2024-08-24 | [44749](https://github.com/airbytehq/airbyte/pull/44749) | Update dependencies |
| 0.2.14 | 2024-08-17 | [44348](https://github.com/airbytehq/airbyte/pull/44348) | Update dependencies |
| 0.2.13 | 2024-08-12 | [43760](https://github.com/airbytehq/airbyte/pull/43760) | Update dependencies |
| 0.2.12 | 2024-08-10 | [43576](https://github.com/airbytehq/airbyte/pull/43576) | Update dependencies |
| 0.2.11 | 2024-08-03 | [43262](https://github.com/airbytehq/airbyte/pull/43262) | Update dependencies |
| 0.2.10 | 2024-07-27 | [42738](https://github.com/airbytehq/airbyte/pull/42738) | Update dependencies |
| 0.2.9 | 2024-07-20 | [42180](https://github.com/airbytehq/airbyte/pull/42180) | Update dependencies |
| 0.2.8 | 2024-07-13 | [41762](https://github.com/airbytehq/airbyte/pull/41762) | Update dependencies |
| 0.2.7 | 2024-07-10 | [41446](https://github.com/airbytehq/airbyte/pull/41446) | Update dependencies |
| 0.2.6 | 2024-07-09 | [41131](https://github.com/airbytehq/airbyte/pull/41131) | Update dependencies |
| 0.2.5 | 2024-07-06 | [40938](https://github.com/airbytehq/airbyte/pull/40938) | Update dependencies |
| 0.2.4 | 2024-06-25 | [40405](https://github.com/airbytehq/airbyte/pull/40405) | Update dependencies |
| 0.2.3 | 2024-06-22 | [40037](https://github.com/airbytehq/airbyte/pull/40037) | Update dependencies |
| 0.2.2 | 2024-06-04 | [39048](https://github.com/airbytehq/airbyte/pull/39048) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.1 | 2024-05-30 | [38136](https://github.com/airbytehq/airbyte/pull/38136) | Make connector compatable with builder |
| 0.2.0 | 2023-10-02 | [30969](https://github.com/airbytehq/airbyte/pull/30969) | Migrated to Low code |
| 0.1.5 | 2022-05-18 | [12942](https://github.com/airbytehq/airbyte/pull/12942) | Fix example inputs |
| 0.1.4 | 2021-12-07 | [8582](https://github.com/airbytehq/airbyte/pull/8582) | Update connector fields title/description |
| 0.1.3 | 2021-12-03 | [8432](https://github.com/airbytehq/airbyte/pull/8432) | Migrate from base_python to CDK, add SAT tests. |
| 0.1.1   | 2020-06-29 | [1046](https://github.com/airbytehq/airbyte/pull/4410)   | Fix runtime UI error from GitHub store path.    |
| 0.1.0   | 2020-05-04 | [1046](https://github.com/airbytehq/airbyte/pull/3149)   | Add source for PokeAPI.                         |

</details>
