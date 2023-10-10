#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import dpath.options

from .abstract_source import AbstractSource
from .config import BaseConfig
from .source import Source

# As part of the CDK sources, we do not control what the APIs return and it is possible that a key is empty.
# Reasons why we are doing this at the airbyte_cdk level:
# * As of today, all the use cases should allow for empty keys
#     * Cases as of 2023-08-31: oauth/session token provider responses, extractor, transformation and substream)
# * The behavior is explicit at the package level and not hidden in every package that needs dpath.options.ALLOW_EMPTY_STRING_KEYS = True
# There is a downside in enforcing this option preemptively in the module __init__.py: the runtime code will import dpath even though the it
# might not need dpath leading to longer initialization time.
# There is a downside in using dpath as a library since the options are global: if we have two pieces of code that want different options,
# this will not be thread-safe.
dpath.options.ALLOW_EMPTY_STRING_KEYS = True

__all__ = ["AbstractSource", "BaseConfig", "Source"]
