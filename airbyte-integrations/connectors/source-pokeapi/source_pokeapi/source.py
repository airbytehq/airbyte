#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

from . import pokemon_list


class PokeapiStream(HttpStream):
    url_base = "https://pokeapi.co/api/v2/"

    def __init__(self, pokemon_name: str, **kwargs):
        super().__init__(**kwargs)
        self.pokemon_name = pokemon_name

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include the Pokemon name as a query param so we do that in this method
        return {"pokemon_name": self.pokemon_name}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        # The response is a simple JSON whose schema matches our stream's schema exactly,
        # so we just return a list containing the response
        return [response.json()]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination,
        # so we return None to indicate there are no more pages in the response
        return None


class Pokemon(PokeapiStream):
    # Set this as a noop.
    primary_key = None

    def path(self, **kwargs) -> str:
        pokemon_name = self.pokemon_name
        return f"pokemon/{pokemon_name}"


# Source
class SourcePokeapi(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        input_pokemon = config["pokemon_name"]
        if input_pokemon not in pokemon_list.POKEMON_LIST:
            return False, f"Input Pokemon {input_pokemon} is invalid. Please check your spelling our input a valid Pokemon."
        else:
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Pokemon(pokemon_name=config["pokemon_name"])]
