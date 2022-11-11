# coding: utf-8
#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pydantic import BaseModel


class TokenModel(BaseModel):
    """Defines a token model."""

    sub: str
