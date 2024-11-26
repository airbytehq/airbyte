from typing import List

from . import _base_key as key


class config:
    """Static class that containes Constants used throughout the libary.
    You can directly use the class-attributes, do not create instances of it!"""

    def __new__(cls):
        raise SyntaxError("you can't create instances of this class")

    INTERRUPT_KEYS: List[str] = [key.CTRL_C]
