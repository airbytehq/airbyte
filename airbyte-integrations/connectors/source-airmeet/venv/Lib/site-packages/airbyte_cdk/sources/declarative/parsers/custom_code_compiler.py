"""Contains functions to compile custom code from text."""

import hashlib
import os
import sys
from collections.abc import Mapping
from types import ModuleType
from typing import Any, cast

from typing_extensions import Literal

ChecksumType = Literal["md5", "sha256"]
CHECKSUM_FUNCTIONS = {
    "md5": hashlib.md5,
    "sha256": hashlib.sha256,
}
COMPONENTS_MODULE_NAME = "components"
SDM_COMPONENTS_MODULE_NAME = "source_declarative_manifest.components"
INJECTED_MANIFEST = "__injected_declarative_manifest"
INJECTED_COMPONENTS_PY = "__injected_components_py"
INJECTED_COMPONENTS_PY_CHECKSUMS = "__injected_components_py_checksums"
ENV_VAR_ALLOW_CUSTOM_CODE = "AIRBYTE_ENABLE_UNSAFE_CODE"


class AirbyteCodeTamperedError(Exception):
    """Raised when the connector's components module does not match its checksum.

    This is a fatal error, as it can be a sign of code tampering.
    """


class AirbyteCustomCodeNotPermittedError(Exception):
    """Raised when custom code is attempted to be run in an environment that does not support it."""

    def __init__(self) -> None:
        super().__init__(
            "Custom connector code is not permitted in this environment. "
            "If you need to run custom code, please ask your administrator to set the `AIRBYTE_ENABLE_UNSAFE_CODE` "
            "environment variable to 'true' in your Airbyte environment. "
            "If you see this message in Airbyte Cloud, your workspace does not allow executing "
            "custom connector code."
        )


def _hash_text(input_text: str, hash_type: str = "md5") -> str:
    """Return the hash of the input text using the specified hash type."""
    if not input_text:
        raise ValueError("Hash input text cannot be empty.")

    hash_object = CHECKSUM_FUNCTIONS[hash_type]()
    hash_object.update(input_text.encode())
    return hash_object.hexdigest()


def custom_code_execution_permitted() -> bool:
    """Return `True` if custom code execution is permitted, otherwise `False`.

    Custom code execution is permitted if the `AIRBYTE_ENABLE_UNSAFE_CODE` environment variable is set to 'true'.
    """
    return os.environ.get(ENV_VAR_ALLOW_CUSTOM_CODE, "").lower() == "true"


def validate_python_code(
    code_text: str,
    checksums: dict[str, str] | None,
) -> None:
    """Validate the provided Python code text against the provided checksums.

    Currently we fail if no checksums are provided, although this may change in the future.
    """
    if not code_text:
        # No code provided, nothing to validate.
        return

    if not checksums:
        raise ValueError(f"A checksum is required to validate the code. Received: {checksums}")

    for checksum_type, checksum in checksums.items():
        if checksum_type not in CHECKSUM_FUNCTIONS:
            raise ValueError(
                f"Unsupported checksum type: {checksum_type}. Supported checksum types are: {CHECKSUM_FUNCTIONS.keys()}"
            )

        calculated_checksum = _hash_text(code_text, checksum_type)
        if calculated_checksum != checksum:
            raise AirbyteCodeTamperedError(
                f"{checksum_type} checksum does not match."
                + str(
                    {
                        "expected_checksum": checksum,
                        "actual_checksum": calculated_checksum,
                        "code_text": code_text,
                    }
                ),
            )


def get_registered_components_module(
    config: Mapping[str, Any] | None,
) -> ModuleType | None:
    """Get a components module object based on the provided config.

    If custom python components is provided, this will be loaded. Otherwise, we will
    attempt to load from the `components` module already imported/registered in sys.modules.

    If custom `components.py` text is provided in config, it will be registered with sys.modules
    so that it can be later imported by manifest declarations which reference the provided classes.

    Returns `None` if no components is provided and the `components` module is not found.
    """
    if config and config.get(INJECTED_COMPONENTS_PY, None):
        if not custom_code_execution_permitted():
            raise AirbyteCustomCodeNotPermittedError

        # Create a new module object and execute the provided Python code text within it
        python_text: str = config[INJECTED_COMPONENTS_PY]
        return register_components_module_from_string(
            components_py_text=python_text,
            checksums=config.get(INJECTED_COMPONENTS_PY_CHECKSUMS, None),
        )

    # Check for `components` or `source_declarative_manifest.components`.
    if SDM_COMPONENTS_MODULE_NAME in sys.modules:
        return cast(ModuleType, sys.modules.get(SDM_COMPONENTS_MODULE_NAME))

    if COMPONENTS_MODULE_NAME in sys.modules:
        return cast(ModuleType, sys.modules.get(COMPONENTS_MODULE_NAME))

    # Could not find module 'components' in `sys.modules`
    # and INJECTED_COMPONENTS_PY was not provided in config.
    return None


def register_components_module_from_string(
    components_py_text: str,
    checksums: dict[str, Any] | None,
) -> ModuleType:
    """Load and return the components module from a provided string containing the python code."""
    # First validate the code
    validate_python_code(
        code_text=components_py_text,
        checksums=checksums,
    )

    # Create a new module object
    components_module = ModuleType(name=COMPONENTS_MODULE_NAME)

    # Execute the module text in the module's namespace
    exec(components_py_text, components_module.__dict__)

    # Register the module in `sys.modules`` so it can be imported as
    # `source_declarative_manifest.components` and/or `components`.
    sys.modules[SDM_COMPONENTS_MODULE_NAME] = components_module
    sys.modules[COMPONENTS_MODULE_NAME] = components_module

    # Now you can import and use the module
    return components_module
