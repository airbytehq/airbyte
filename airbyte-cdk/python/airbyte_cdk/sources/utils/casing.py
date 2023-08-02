#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import re


# https://stackoverflow.com/a/1176023
def camel_to_snake(s: str) -> str:
    s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()
