#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pipelines.helpers.utils import slugify


def get_ruff_cache_key(ruff_version: str) -> str:
    return slugify(f"ruff-{ruff_version}")


def get_prettier_cache_key(prettier_version: str) -> str:
    return slugify(f"prettier-{prettier_version}")
