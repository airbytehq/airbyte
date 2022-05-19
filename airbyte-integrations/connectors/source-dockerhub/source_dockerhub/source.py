from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from . import pokemon_list

class SourceDockerhub(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        username = config["docker_username"]

        # get JWT
        jwt_url = "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/alpine:pull"
        response = requests.get(jwt_url)
        jwt = response.json()["token"]


        # check that jwt is valid and that username is valid
        url = f"https://hub.docker.com/v2/repositories/{username}/"
        auth = TokenAuthenticator(token=jwt)
        try:
            # response = requests.get(url, headers=auth.get_auth_header())
            response = requests.get(url, headers={"Authorization": jwt})
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print(str(e))
                return False, "Invalid JWT received, check if auth.docker.io changed API"
            elif e.response.status_code == 404:
                print(str(e))
                return False, f"User '{username}' not found"
            else:
                print(str(e))
                return False, f"Error getting basic user info for Docker user '{username}', unexepcted error"
        json_response = response.json()
        repocount = json_response["count"]
        print(f"Connection check for Docker user '{username}' successful: {repocount} repos found")
        return True, None


        input_pokemon = config["pokemon_name"]
        if input_pokemon not in pokemon_list.POKEMON_LIST:
            return False, f"Input Pokemon {input_pokemon} is invalid. Please check your spelling and input a valid Pokemon."
        else:
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [Pokemon(pokemon_name=config["pokemon_name"])]

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