#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.file_based.config.abstract_file_based_spec import (
    AbstractFileBasedSpec,
    DeliverRawFiles,
)
from airbyte_cdk.sources.specs.transfer_modes import DeliverPermissions

DELIVERY_TYPE_KEY = "delivery_type"
DELIVERY_TYPE_PERMISSION_TRANSFER_MODE_VALUE = "use_permissions_transfer"
DELIVERY_TYPE_FILES_TRANSFER_MODE_VALUE = "use_file_transfer"
PRESERVE_DIRECTORY_STRUCTURE_KEY = "preserve_directory_structure"
INCLUDE_IDENTITIES_STREAM_KEY = "include_identities_stream"


def use_file_transfer(parsed_config: AbstractFileBasedSpec) -> bool:
    """Returns `True` if the configuration uses file transfer mode."""
    return (
        hasattr(parsed_config.delivery_method, DELIVERY_TYPE_KEY)
        and parsed_config.delivery_method.delivery_type == DELIVERY_TYPE_FILES_TRANSFER_MODE_VALUE
    )


def preserve_directory_structure(parsed_config: AbstractFileBasedSpec) -> bool:
    """
    Determines whether to preserve directory structure during file transfer.

    When enabled, files maintain their subdirectory paths in the destination.
    When disabled, files are flattened to the root of the destination.

    Args:
        parsed_config: The parsed configuration containing delivery method settings

    Returns:
        True if directory structure should be preserved (default), False otherwise
    """
    if (
        use_file_transfer(parsed_config)
        and hasattr(parsed_config.delivery_method, PRESERVE_DIRECTORY_STRUCTURE_KEY)
        and isinstance(parsed_config.delivery_method, DeliverRawFiles)
    ):
        return parsed_config.delivery_method.preserve_directory_structure
    return True


def use_permissions_transfer(parsed_config: AbstractFileBasedSpec) -> bool:
    """
    Determines whether to use permissions transfer to sync ACLs and Identities

    Args:
        parsed_config: The parsed configuration containing delivery method settings

    Returns:
        True if permissions transfer should be enabled, False otherwise
    """
    return (
        hasattr(parsed_config.delivery_method, DELIVERY_TYPE_KEY)
        and parsed_config.delivery_method.delivery_type
        == DELIVERY_TYPE_PERMISSION_TRANSFER_MODE_VALUE
    )


def include_identities_stream(parsed_config: AbstractFileBasedSpec) -> bool:
    """
    There are scenarios where user may not have access to identities but still is valuable to get ACLs

    Args:
        parsed_config: The parsed configuration containing delivery method settings

    Returns:
        True if we should include Identities stream.
    """
    if (
        use_permissions_transfer(parsed_config)
        and hasattr(parsed_config.delivery_method, INCLUDE_IDENTITIES_STREAM_KEY)
        and isinstance(parsed_config.delivery_method, DeliverPermissions)
    ):
        return parsed_config.delivery_method.include_identities_stream
    return False
