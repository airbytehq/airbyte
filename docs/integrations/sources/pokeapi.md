# PokéAPI

## Tutorials

The PokéAPI is primarly used as a tutorial and educational resource, as it requires zero dependencies. Learn how Airbyte and this connector works with these tutorials:

- [Airbyte Quickstart: An Introduction to Deploying and Syncing](/platform/using-airbyte/getting-started/oss-quickstart)
- [Using Connector Builder and the low-code CDK](/platform/connector-development/connector-builder-ui/overview)
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
| 0.3.45 | 2025-12-09 | [70514](https://github.com/airbytehq/airbyte/pull/70514) | Update dependencies |
| 0.3.44 | 2025-11-25 | [69964](https://github.com/airbytehq/airbyte/pull/69964) | Update dependencies |
| 0.3.43 | 2025-11-18 | [69659](https://github.com/airbytehq/airbyte/pull/69659) | Update dependencies |
| 0.3.42 | 2025-10-29 | [68928](https://github.com/airbytehq/airbyte/pull/68928) | Update dependencies |
| 0.3.41 | 2025-10-21 | [68252](https://github.com/airbytehq/airbyte/pull/68252) | Update dependencies |
| 0.3.40 | 2025-10-14 | [67489](https://github.com/airbytehq/airbyte/pull/67489) | Update dependencies |
| 0.3.39 | 2025-09-30 | [66956](https://github.com/airbytehq/airbyte/pull/66956) | Update dependencies |
| 0.3.38 | 2025-09-23 | [66412](https://github.com/airbytehq/airbyte/pull/66412) | Update dependencies |
| 0.3.37 | 2025-09-09 | [65871](https://github.com/airbytehq/airbyte/pull/65871) | Update dependencies |
| 0.3.36 | 2025-08-23 | [65223](https://github.com/airbytehq/airbyte/pull/65223) | Update dependencies |
| 0.3.35 | 2025-08-09 | [64702](https://github.com/airbytehq/airbyte/pull/64702) | Update dependencies |
| 0.3.34 | 2025-08-02 | [64212](https://github.com/airbytehq/airbyte/pull/64212) | Update dependencies |
| 0.3.33 | 2025-07-31 | [64147](https://github.com/airbytehq/airbyte/pull/64147) | Update dependencies |
| 0.3.32 | 2025-07-26 | [63873](https://github.com/airbytehq/airbyte/pull/63873) | Update dependencies |
| 0.3.31 | 2025-07-19 | [63428](https://github.com/airbytehq/airbyte/pull/63428) | Update dependencies |
| 0.3.30 | 2025-07-12 | [63262](https://github.com/airbytehq/airbyte/pull/63262) | Update dependencies |
| 0.3.29 | 2025-07-05 | [62562](https://github.com/airbytehq/airbyte/pull/62562) | Update dependencies |
| 0.3.28 | 2025-06-28 | [62408](https://github.com/airbytehq/airbyte/pull/62408) | Update dependencies |
| 0.3.27 | 2025-06-26 | [62103](https://github.com/airbytehq/airbyte/pull/62103) | Fix `nidoran` names |
| 0.3.26 | 2025-06-21 | [61935](https://github.com/airbytehq/airbyte/pull/61935) | Update dependencies |
| 0.3.25 | 2025-06-14 | [61063](https://github.com/airbytehq/airbyte/pull/61063) | Update dependencies |
| 0.3.24 | 2025-05-24 | [60437](https://github.com/airbytehq/airbyte/pull/60437) | Update dependencies |
| 0.3.23 | 2025-05-10 | [60084](https://github.com/airbytehq/airbyte/pull/60084) | Update dependencies |
| 0.3.22 | 2025-05-03 | [59486](https://github.com/airbytehq/airbyte/pull/59486) | Update dependencies |
| 0.3.21 | 2025-04-27 | [59102](https://github.com/airbytehq/airbyte/pull/59102) | Update dependencies |
| 0.3.20 | 2025-04-19 | [58517](https://github.com/airbytehq/airbyte/pull/58517) | Update dependencies |
| 0.3.19 | 2025-04-12 | [57849](https://github.com/airbytehq/airbyte/pull/57849) | Update dependencies |
| 0.3.18 | 2025-04-05 | [57292](https://github.com/airbytehq/airbyte/pull/57292) | Update dependencies |
| 0.3.17 | 2025-03-29 | [56733](https://github.com/airbytehq/airbyte/pull/56733) | Update dependencies |
| 0.3.16 | 2025-03-22 | [56172](https://github.com/airbytehq/airbyte/pull/56172) | Update dependencies |
| 0.3.15 | 2025-03-08 | [55569](https://github.com/airbytehq/airbyte/pull/55569) | Update dependencies |
| 0.3.14 | 2025-03-01 | [55073](https://github.com/airbytehq/airbyte/pull/55073) | Update dependencies |
| 0.3.13 | 2025-02-23 | [54598](https://github.com/airbytehq/airbyte/pull/54598) | Update dependencies |
| 0.3.12 | 2025-02-15 | [54015](https://github.com/airbytehq/airbyte/pull/54015) | Update dependencies |
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
