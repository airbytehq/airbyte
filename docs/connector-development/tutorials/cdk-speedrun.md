# Python CDK Speedrun: Creating a Source

## CDK Speedrun \(HTTP API Source Creation Any Route\)

This is a blazing fast guide to building an HTTP source connector. Think of it as the TL;DR version
of [this tutorial.](custom-python-connector/0-getting-started.md)

If you are a visual learner and want to see a video version of this guide going over each part in
detail, check it out below.

[A speedy CDK overview.](https://www.youtube.com/watch?v=kJ3hLoNfz_E)

## Dependencies

1. Python &gt;= 3.9
2. [Poetry](https://python-poetry.org/)
3. Docker

#### Generate the Template

```bash
# # clone the repo if you havent already
# git clone --depth 1 https://github.com/airbytehq/airbyte/
# cd airbyte # start from repo root
cd airbyte-integrations/connector-templates/generator
./generate.sh
```

Select the `Python CDK Source` and name it `python-http-example`.

#### Create Dev Environment

```bash
cd ../../connectors/source-python-http-example
poetry install
```

### Define Connector Inputs

```bash
cd source_python_http_example
```

We're working with the PokeAPI, so we need to define our input schema to reflect that. Open the
`spec.yaml` file here and replace it with:

```yaml
documentationUrl: https://docs.airbyte.com/integrations/sources/pokeapi
connectionSpecification:
  $schema: http://json-schema.org/draft-07/schema#
  title: Pokeapi Spec
  type: object
  required:
    - pokemon_name
  properties:
    pokemon_name:
      type: string
      description: Pokemon requested from the API.
      pattern: ^[a-z0-9_\-]+$
      examples:
        - ditto
        - luxray
        - snorlax
```

As you can see, we have one input to our input schema, which is `pokemon_name`, which is required.
Normally, input schemas will contain information such as API keys and client secrets that need to
get passed down to all endpoints or streams.

Ok, let's write a function that checks the inputs we just defined. Nuke the `source.py` file. Now
add this code to it. For a crucial time skip, we're going to define all the imports we need in the
future here. Also note that your `AbstractSource` class name must be a camel-cased version of the
name you gave in the generation phase. In our case, this is `SourcePythonHttpExample`.

```python
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import logging
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

from . import pokemon_list

logger = logging.getLogger("airbyte")

class SourcePythonHttpExample(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        logger.info("Checking Pokemon API connection...")
        input_pokemon = config["pokemon_name"]
        if input_pokemon not in pokemon_list.POKEMON_LIST:
            result = f"Input Pokemon {input_pokemon} is invalid. Please check your spelling and input a valid Pokemon."
            logger.info(f"PokeAPI connection failed: {result}")
            return False, result
        else:
            logger.info(f"PokeAPI connection success: {input_pokemon} is a valid Pokemon")
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Pokemon(pokemon_name=config["pokemon_name"])]
```

Create a new file called `pokemon_list.py` at the same level. This will handle input validation for
us so that we don't input invalid Pokemon. Let's start with a very limited list - any Pokemon not
included in this list will get rejected.

```python
"""
pokemon_list.py includes a list of all known pokemon for config validation in source.py.
"""

POKEMON_LIST = [
    "bulbasaur",
    "charizard",
    "wartortle",
    "pikachu",
    "crobat",
]
```

Test it.

```bash
cd ..
mkdir sample_files
echo '{"pokemon_name": "pikachu"}'  > sample_files/config.json
echo '{"pokemon_name": "chikapu"}'  > sample_files/invalid_config.json
poetry run source-python-http-example check --config sample_files/config.json
poetry run source-python-http-example check --config sample_files/invalid_config.json
```

Expected output:

```bash
> poetry run source-python-http-example check --config sample_files/config.json
{"type": "CONNECTION_STATUS", "connectionStatus": {"status": "SUCCEEDED"}}

> poetry run source-python-http-example check --config sample_files/invalid_config.json
{"type": "CONNECTION_STATUS", "connectionStatus": {"status": "FAILED", "message": "'Input Pokemon chikapu is invalid. Please check your spelling our input a valid Pokemon.'"}}
```

### Define your Stream

In your `source.py` file, add this `Pokemon` class. This stream represents an endpoint you want to
hit, which in our case, is the single [Pokemon endpoint](https://pokeapi.co/docs/v2#pokemon).

```python
class Pokemon(HttpStream):
    url_base = "https://pokeapi.co/api/v2/"

    # Set this as a noop.
    primary_key = None

    def __init__(self, pokemon_name: str, **kwargs):
        super().__init__(**kwargs)
        self.pokemon_name = pokemon_name

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination, so we return None to indicate there are no more pages in the response
        return None

    def path(
        self,
    ) -> str:
        return ""  # TODO

    def parse_response(
        self,
    ) -> Iterable[Mapping]:
        return None  # TODO
```

Now download [this file](./cdk-speedrun-assets/pokemon.json). Name it `pokemon.json` and place it in
`/source_python_http_example/schemas`.

This file defines your output schema for every endpoint that you want to implement. Normally, this
will likely be the most time-consuming section of the connector development process, as it requires
defining the output of the endpoint exactly. This is really important, as Airbyte needs to have
clear expectations for what the stream will output. Note that the name of this stream will be
consistent in the naming of the JSON schema and the `HttpStream` class, as `pokemon.json` and
`Pokemon` respectively in this case. Learn more about schema creation
[here](https://docs.airbyte.com/connector-development/cdk-python/full-refresh-stream#defining-the-streams-schema).

Test your discover function. You should receive a fairly large JSON object in return.

```bash
poetry run source-python-http-example discover --config sample_files/config.json
```

Note that our discover function is using the `pokemon_name` config variable passed in from the
`Pokemon` stream when we set it in the `__init__` function.

### Reading Data from the Source

Update your `Pokemon` class to implement the required functions as follows:

```python
class Pokemon(HttpStream):
    url_base = "https://pokeapi.co/api/v2/"

    # Set this as a noop.
    primary_key = None

    def __init__(self, pokemon_name: str, **kwargs):
        super().__init__(**kwargs)
        # Here's where we set the variable from our input to pass it down to the source.
        self.pokemon_name = pokemon_name

    def path(self, **kwargs) -> str:
        pokemon_name = self.pokemon_name
        # This defines the path to the endpoint that we want to hit.
        return f"pokemon/{pokemon_name}"

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include the Pokemon name as a query param so we do that in this method.
        return {"pokemon_name": self.pokemon_name}

    def parse_response(
            self,
            response: requests.Response,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        # The response is a simple JSON whose schema matches our stream's schema exactly,
        # so we just return a list containing the response.
        return [response.json()]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # While the PokeAPI does offer pagination, we will only ever retrieve one Pokemon with this implementation,
        # so we just return None to indicate that there will never be any more pages in the response.
        return None
```

We now need a catalog that defines all of our streams. We only have one stream: `Pokemon`. Download
that file [here](./cdk-speedrun-assets/configured_catalog_pokeapi.json). Place it in `/sample_files`
named as `configured_catalog.json`. More clearly, this is where we tell Airbyte all the
streams/endpoints we support for the connector and in which sync modes Airbyte can run the connector
on. Learn more about the AirbyteCatalog
[here](https://docs.airbyte.com/understanding-airbyte/beginners-guide-to-catalog) and learn more
about sync modes [here](https://docs.airbyte.com/understanding-airbyte/connections#sync-modes).

Let's read some data.

```bash
poetry run source-python-http-example read --config sample_files/config.json --catalog sample_files/configured_catalog.json
```

If all goes well, containerize it so you can use it in the UI:

**Option A: Building the docker image with `airbyte-ci`**

This is the preferred method for building and testing connectors.

If you want to open source your connector we encourage you to use our
[`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
tool to build your connector. It will not use a Dockerfile but will build the connector image from
our
[base image](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/base_images/README.md)
and use our internal build logic to build an image from your Python connector code.

Running `airbyte-ci connectors --name source-<source-name> build` will build your connector image.
Once the command is done, you will find your connector image in your local docker host:
`airbyte/source-<source-name>:dev`.

**Option B: Building the docker image with a Dockerfile**

If you don't want to rely on `airbyte-ci` to build your connector, you can build the docker image
using your own Dockerfile. This method is not preferred, and is not supported for certified
connectors.

Create a `Dockerfile` in the root of your connector directory. The `Dockerfile` should look
something like this:

```Dockerfile

FROM airbyte/python-connector-base:1.1.0

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```

Please use this as an example. This is not optimized.

Build your image:

```bash
docker build . -t airbyte/source-example-python:dev
```

You're done. Stop the clock :\)

## Further reading

If you have enjoyed the above example, and would like to explore the Python CDK in even more detail,
you may be interested looking at
[how to build a connector to extract data from the Webflow API](https://airbyte.com/tutorials/extract-data-from-the-webflow-api)
