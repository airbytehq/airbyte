#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from dataclasses import dataclass


@dataclass
class DeclarativeAuthenticator(ABC):
    """
    Interface used to associate which authenticators can be used as part of the declarative framework
    """
