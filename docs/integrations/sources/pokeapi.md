# PokéAPI

## Tutorials

The PokéAPI is primarly used as a tutorial and educational resource, as it requires zero dependencies. Learn how Airbyte and this connector works with these tutorials:

* [Airbyte Quickstart: An Introduction to Deploying and Syncing](../../quickstart/deploy-airbyte.md)
* [Airbyte CDK Speedrun: A Quick Primer on Building Source Connectors](../../connector-development/tutorials/cdk-speedrun.md)
* [How to Build ETL Sources in Under 30 Minutes: A Video Tutorial](https://www.youtube.com/watch?v=kJ3hLoNfz_E&t=13s&ab_channel=Airbyte)

## Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| Replicate Incremental Deletes | No |
| SSL connection | No |
| Namespaces | No |

This source uses the fully open [PokéAPI](https://pokeapi.co/docs/v2#info) to serve and retrieve information about Pokémon. This connector should be primarily used for educational purposes or for getting a trial source up and running without needing any dependencies. As this API is fully open and is not rate-limited, no authentication or rate-limiting is performed, so you can use this connector right out of the box without any further configuration.

## Output Schema

Currently, only one output stream is available from this source, which is the Pokémon output stream. This schema is defined [here](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-pokeapi/source_pokeapi/schemas/pokemon.json).

## Rate Limiting & Performance Considerations (Airbyte Open-Source)

According to the API's [fair use policy](https://pokeapi.co/docs/v2#fairuse), please make sure to cache resources retrieved from the PokéAPI wherever possible. That said, the PokéAPI does not perform rate limiting.

## Data Type Mapping

The PokéAPI uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.1   | 2020-06-29 | [1046](https://github.com/airbytehq/airbyte/pull/4410) | Fix runtime UI error from GitHub store path. |
| 0.1.0   | 2020-05-04 | [1046](https://github.com/airbytehq/airbyte/pull/3149) | Add source for PokeAPI. |

