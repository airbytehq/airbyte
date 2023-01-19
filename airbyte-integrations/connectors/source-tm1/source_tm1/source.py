from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import logging
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

from . import pokemon_list

logger = logging.getLogger("airbyte")

class SourceTM1(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        logger.info("Checking TM1 API connection...")
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