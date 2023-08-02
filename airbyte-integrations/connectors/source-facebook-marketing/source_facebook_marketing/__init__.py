#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from facebook_business import api

from .streams.patches import CursorPatch

# This is a monkey patch to override Facebook SDK Cursor's default behaviour, so we could use retry patterns
# to retry any individual request. See more in the docstring of a CursorPatch class.
api.Cursor = CursorPatch

from .source import SourceFacebookMarketing  # noqa: E402

__all__ = ["SourceFacebookMarketing"]
