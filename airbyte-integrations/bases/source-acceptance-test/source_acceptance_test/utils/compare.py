#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import json
from typing import List, Mapping, Optional

import icdiff
import py
from pprintpp import pformat

MAX_COLS = py.io.TerminalWriter().fullwidth
MARGIN_LEFT = 20
GUTTER = 3
MARGINS = MARGIN_LEFT + GUTTER + 1


def diff_dicts(left, right, use_markup) -> Optional[List[str]]:
    half_cols = MAX_COLS / 2 - MARGINS

    pretty_left = pformat(left, indent=1, width=half_cols).splitlines()
    pretty_right = pformat(right, indent=1, width=half_cols).splitlines()
    diff_cols = MAX_COLS - MARGINS

    if len(pretty_left) < 3 or len(pretty_right) < 3:
        # avoid small diffs far apart by smooshing them up to the left
        smallest_left = pformat(left, indent=2, width=1).splitlines()
        smallest_right = pformat(right, indent=2, width=1).splitlines()
        max_side = max(len(line) + 1 for line in smallest_left + smallest_right)
        if (max_side * 2 + MARGIN_LEFT) < MAX_COLS:
            diff_cols = max_side * 2 + GUTTER
            pretty_left = pformat(left, indent=2, width=max_side).splitlines()
            pretty_right = pformat(right, indent=2, width=max_side).splitlines()

    differ = icdiff.ConsoleDiff(cols=diff_cols, tabsize=2)

    if not use_markup:
        # colorization is disabled in Pytest - either due to the terminal not
        # supporting it or the user disabling it. We should obey, but there is
        # no option in icdiff to disable it, so we replace its colorization
        # function with a no-op
        differ.colorize = lambda string: string
        color_off = ""
    else:
        color_off = icdiff.color_codes["none"]

    icdiff_lines = list(differ.make_table(pretty_left, pretty_right, context=True))

    return ["equals failed"] + [color_off + line for line in icdiff_lines]


class DictWithHash(dict):

    _hash: str = None

    def __hash__(self):
        if not self._hash:
            self._hash = hash(json.dumps({k: serialize(v) for k, v in self.items()}, sort_keys=True))
        return self._hash

    def __lt__(self, other):
        return hash(self) < hash(other)


def serialize(value) -> str:
    """Simplify comparison of nested dicts/lists"""
    if isinstance(value, Mapping):
        return DictWithHash(value)
    if isinstance(value, List):
        return sorted([serialize(v) for v in value])
    return str(value)
