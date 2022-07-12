#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import TypedDict


class Spec(TypedDict):
    aws_access_key_id: str
    aws_secret_access_key: str
    region_name: str
