from typing import Dict, Type

from .base import PoeExecutor


class SimpleExecutor(PoeExecutor):
    """
    A poe executor implementation that executes tasks without doing any special setup.
    """

    __key__ = "simple"
    __options__: Dict[str, Type] = {}
