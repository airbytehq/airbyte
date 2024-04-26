from typing import Any, Mapping, Optional, Union
from airbyte_cdk.models import FailureType
from .response_action import ResponseAction

class ErrorMapping:

    DEFAULT_ERROR_MAPPING: Mapping[Union[int, str], Mapping[str, Any]] = {
        400: { "action": ResponseAction.FAIL, "failure_type": FailureType.config_error, "error_message": "Placeholder error message for 400 -- TBD" },
        401: { "action": ResponseAction.FAIL, "failure_type": FailureType.config_error },
        403: { "action": ResponseAction.FAIL, "failure_type": FailureType.config_error },
        404: { "action": ResponseAction.FAIL, "failure_type": FailureType.system_error },
        408: { "action": ResponseAction.FAIL, "failure_type": FailureType.transient_error },
        429: { "action": ResponseAction.FAIL, "failure_type": FailureType.transient_error },
        500: { "action": ResponseAction.RETRY, "failure_type": FailureType.transient_error },
        502: { "action": ResponseAction.RETRY, "failure_type": FailureType.transient_error },
        503: { "action": ResponseAction.RETRY, "failure_type": FailureType.transient_error },
    }

    def __init__(self, error_mapping: Optional[Mapping[Union[int, str], Mapping[str, Any]]] = None) -> None:
        """
        Initialize the ErrorMapping.

        :param error_mapping: Custom error mappings to extend or override the default mappings.
        """
        self.error_mapping = dict(self.DEFAULT_ERROR_MAPPING)
        if error_mapping:
            self.error_mapping.update(error_mapping)

    def get_error_mapping(self, key: Union[int, str]) -> Optional[Mapping[str, Any]]:
        """
        Get the error mapping for the specified key.

        :param key: The key to look up in the error mapping.
        :return: The error mapping for the specified key, or None if not found.
        """
        return self.error_mapping.get(key)

    def update_error_mapping(self, error_mapping: Mapping[Union[int, str], Mapping[str, Any]]) -> None:
        """
        Update the error mapping with the provided mappings.

        :param error_mapping: Custom error mappings to extend or override the default mappings.
        """
        self.error_mapping.update(error_mapping)
