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
| 0.2.2 | 2024-06-04 | [39048](https://github.com/airbytehq/airbyte/pull/39048) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.1 | 2024-05-30 | [38136](https://github.com/airbytehq/airbyte/pull/38136) | Make connector compatable with builder |
| 0.2.0 | 2023-10-02 | [30969](https://github.com/airbytehq/airbyte/pull/30969) | Migrated to Low code |
| 0.1.5 | 2022-05-18 | [12942](https://github.com/airbytehq/airbyte/pull/12942) | Fix example inputs |
| 0.1.4 | 2021-12-07 | [8582](https://github.com/airbytehq/airbyte/pull/8582) | Update connector fields title/description |
| 0.1.3 | 2021-12-03 | [8432](https://github.com/airbytehq/airbyte/pull/8432) | Migrate from base_python to CDK, add SAT tests. |
| 0.1.1   | 2020-06-29 | [1046](https://github.com/airbytehq/airbyte/pull/4410)   | Fix runtime UI error from GitHub store path.    |
| 0.1.0   | 2020-05-04 | [1046](https://github.com/airbytehq/airbyte/pull/3149)   | Add source for PokeAPI.                         |

</details>