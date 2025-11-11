#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import BufferedIOBase
from typing import Any, Dict, Generator, List, MutableMapping, Optional, Set, Tuple

logger = logging.getLogger("airbyte")


PARSER_OUTPUT_TYPE = Generator[MutableMapping[str, Any], None, None]


@dataclass
class Parser(ABC):
    @abstractmethod
    def parse(self, data: BufferedIOBase) -> PARSER_OUTPUT_TYPE:
        """
        Parse data and yield dictionaries.
        """
        pass


# reusable parser types
PARSERS_TYPE = List[Tuple[Set[str], Set[str], Parser]]
PARSERS_BY_HEADER_TYPE = Optional[Dict[str, Dict[str, Parser]]]
