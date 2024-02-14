# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Secrets management for AirbyteLib."""
from __future__ import annotations

import contextlib
import os
from enum import Enum, auto
from getpass import getpass
from typing import TYPE_CHECKING

from dotenv import dotenv_values

from airbyte_lib import exceptions as exc


if TYPE_CHECKING:
    from collections.abc import Callable


try:
    from google.colab import userdata as colab_userdata
except ImportError:
    colab_userdata = None


class SecretSource(Enum):
    ENV = auto()
    DOTENV = auto()
    GOOGLE_COLAB = auto()
    ANY = auto()

    PROMPT = auto()


def _get_secret_from_env(
    secret_name: str,
) -> str | None:
    if secret_name not in os.environ:
        return None

    return os.environ[secret_name]


def _get_secret_from_dotenv(
    secret_name: str,
) -> str | None:
    try:
        dotenv_vars: dict[str, str | None] = dotenv_values()
    except Exception:
        # Can't locate or parse a .env file
        return None

    if secret_name not in dotenv_vars:
        # Secret not found
        return None

    return dotenv_vars[secret_name]


def _get_secret_from_colab(
    secret_name: str,
) -> str | None:
    if colab_userdata is None:
        # The module doesn't exist. We probably aren't in Colab.
        return None

    try:
        return colab_userdata.get(secret_name)
    except Exception:
        # Secret name not found. Continue.
        return None


def _get_secret_from_prompt(
    secret_name: str,
) -> str | None:
    with contextlib.suppress(Exception):
        return getpass(f"Enter the value for secret '{secret_name}': ")

    return None


_SOURCE_FUNCTIONS: dict[SecretSource, Callable] = {
    SecretSource.ENV: _get_secret_from_env,
    SecretSource.DOTENV: _get_secret_from_dotenv,
    SecretSource.GOOGLE_COLAB: _get_secret_from_colab,
    SecretSource.PROMPT: _get_secret_from_prompt,
}


def get_secret(
    secret_name: str,
    source: SecretSource | list[SecretSource] = SecretSource.ANY,
    *,
    prompt: bool = True,
) -> str:
    """Get a secret from the environment.

    The optional `source` argument of enum type `SecretSource` or list of `SecretSource` options.
    If left blank, the `source` arg will be `SecretSource.ANY`. If `source` is set to a specific
    source, then only that source will be checked. If a list of `SecretSource` entries is passed,
    then the sources will be checked using the provided ordering.

    If `prompt` to `True` or if SecretSource.PROMPT is declared in the `source` arg, then the
    user will be prompted to enter the secret if it is not found in any of the other sources.
    """
    sources = [source] if not isinstance(source, list) else source
    all_sources = set(_SOURCE_FUNCTIONS.keys()) - {SecretSource.PROMPT}
    if SecretSource.ANY in sources:
        sources += [s for s in all_sources if s not in sources]
        sources.remove(SecretSource.ANY)

    if prompt or SecretSource.PROMPT in sources:
        if SecretSource.PROMPT in sources:
            sources.remove(SecretSource.PROMPT)

        sources.append(SecretSource.PROMPT)  # Always check prompt last

    for source in sources:
        fn = _SOURCE_FUNCTIONS[source]  # Get the matching function for this source
        val = fn(secret_name)
        if val:
            return val

    raise exc.AirbyteLibSecretNotFoundError(
        secret_name=secret_name,
        sources=[str(s) for s in sources],
    )
