# fmt: off
from typing import Union

import rich.box
from rich.box import Box


HORIZONTALS_TOP: Box = Box(
    " ── \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
)

HORIZONTALS_DOUBLE_TOP: Box = Box(
    " ══ \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
)

BLANK: Box = Box(
    "    \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
    "    \n"
)

BLANK.top = ""
BLANK.top_left = ""
BLANK.top_right = " " * 800  # Reasonably ensure padding
BLANK.top_divider = ""

def get_box(box: Union[str, Box]) -> Box:
    """Retrieve a Rich Box by name."""
    if isinstance(box, Box):
        return box
    if box == box.upper() and box in globals():
        return globals()[box]  # type: ignore[no-any-return]
    return getattr(rich.box, box)  # type: ignore[no-any-return]
