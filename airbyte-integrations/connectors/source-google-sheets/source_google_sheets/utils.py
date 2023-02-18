#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import re

import unidecode

TOKEN_PATTERN = re.compile(r"[A-Z]+[a-z]*|[a-z]+|\d+|(?P<NoToken>[^a-zA-Z\d]+)")
DEFAULT_SEPARATOR = "_"


def name_conversion(text):
    """
    https://fivetran.com/docs/getting-started/core-concepts#tableandcolumnnamingruleset
    """
    text = unidecode.unidecode(text)

    tokens = []
    for m in TOKEN_PATTERN.finditer(text):
        if m.group("NoToken") is None:
            tokens.append(m.group(0))
        else:
            tokens.append("")

    if len(tokens) >= 3:
        tokens = tokens[:1] + [t for t in tokens[1:-1] if t] + tokens[-1:]

    if tokens and tokens[0].isdigit():
        tokens.insert(0, "")

    text = DEFAULT_SEPARATOR.join(tokens)
    text = text.lower()
    return text


def safe_name_conversion(text):
    text = name_conversion(text)
    if not text:
        raise Exception(f"initial string '{text}' converted to empty")
    return text
