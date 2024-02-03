# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Secrets management for AirbyteLib."""
from __future__ import annotations

import os
from enum import Enum, auto

from airbyte_lib import exceptions as exc


class SecretSource(Enum):
    ENV = auto()
    GOOGLE_COLAB = auto()
    ANY = auto()


ALL_SOURCES = [
    SecretSource.ENV,
    SecretSource.GOOGLE_COLAB,
]


try:
    from google.colab import userdata as colab_userdata
except ImportError:
    colab_userdata = None


def get_secret(
    secret_name: str, source: SecretSource | list[SecretSource] = SecretSource.ANY
) -> str:
    """Get a secret from the environment.

    The optional `source` argument of enum type `SecretSource` or list of `SecretSource` options.
    If left blank, the `source` arg will be `SecretSource.ANY`. If `source` is set to a specific
    source, then only that source will be checked. If a list of `SecretSource` entries is passed,
    then the sources will be checked using the provided ordering.
    """
    sources = [source] if not isinstance(source, list) else source
    for s in sources:
        val = _get_secret_from_source(secret_name, s)
        if val:
            return val

    raise exc.AirbyteLibSecretNotFoundError(
        secret_name=secret_name,
        sources=[str(s) for s in sources],
    )


def _get_secret_from_source(
    secret_name: str,
    source: SecretSource,
) -> str | None:
    if source in [SecretSource.ENV, SecretSource.ANY] and secret_name in os.environ:
        return os.environ[secret_name]

    if (
        source in [SecretSource.GOOGLE_COLAB, SecretSource.ANY]
        and colab_userdata is not None
        and colab_userdata.get(secret_name, None)
    ):
        return colab_userdata.get(secret_name)

    return None
