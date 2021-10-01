# PokéAPI

## Overview

The PokéAPI source currently supports only Full Refresh syncs.

This source uses the fully open [PokéAPI](https://pokeapi.co/docs/v2#info) to serve and retrieve information about Pokémon. This connector should be primarily used for educational purposes or for getting a trial source up and running without needing any dependencies.

### Output schema

Currently, only one output stream is available from this source, which is the Pokémon output stream. This schema is defined [here](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-pokeapi/source_pokeapi/schemas/pokemon.json).

### Data type mapping

The PokéAPI uses the same [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html) types that Airbyte uses internally \(`string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number`\), so no type conversions happen as part of this source.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| Replicate Incremental Deletes | No |
| SSL connection | No |
| Namespaces | No |

### Performance considerations

According to the API's [fair use policy](https://pokeapi.co/docs/v2#fairuse), please make sure to cache resources retrieved from the PokéAPI wherever possible.

## Dependencies/Requirements

* As this API is fully open and is not rate-limited, no authentication or rate-limiting is performed, so you can use this connector right out of the box without any further configuration.

