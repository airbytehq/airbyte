#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pipelines.helpers.utils import slugify


def get_black_cache_key(black_version: str) -> str:
    return slugify(f"black-{black_version}")


def get_prettier_cache_key(prettier_version: str) -> str:
    return slugify(f"prettier-{prettier_version}")
