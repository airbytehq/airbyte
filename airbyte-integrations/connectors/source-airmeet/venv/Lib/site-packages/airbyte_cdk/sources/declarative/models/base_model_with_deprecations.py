# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

# THIS IS A STATIC CLASS MODEL USED TO DISPLAY DEPRECATION WARNINGS
# WHEN DEPRECATED FIELDS ARE ACCESSED

import warnings

# ignore the SyntaxWarning in the Airbyte log messages, during the string evaluation
warnings.filterwarnings("ignore", category=SyntaxWarning)

from typing import Any, List

from pydantic.v1 import BaseModel

from airbyte_cdk.connector_builder.models import LogMessage as ConnectorBuilderLogMessage

# format the warning message
warnings.formatwarning = (
    lambda message, category, *args, **kwargs: f"{category.__name__}: {message}\n"
)


FIELDS_TAG = "__fields__"
DEPRECATED = "deprecated"
DEPRECATION_MESSAGE = "deprecation_message"
DEPRECATION_LOGS_TAG = "_deprecation_logs"


class BaseModelWithDeprecations(BaseModel):
    """
    Pydantic BaseModel that warns when deprecated fields are accessed.
    The deprecation message is stored in the field's extra attributes.
    This class is used to create models that can have deprecated fields
    and show warnings when those fields are accessed or initialized.

    The `_deprecation_logs` attribute is stored in the model itself.
    The collected deprecation warnings are further propagated to the Airbyte log messages,
    during the component creation process, in `model_to_component._collect_model_deprecations()`.

    The component implementation is not responsible for handling the deprecation warnings,
    since the deprecation warnings are already handled in the model itself.
    """

    class Config:
        """
        Allow extra fields in the model. In case the model restricts extra fields.
        """

        extra = "allow"

    def __init__(self, **model_fields: Any) -> None:
        """
        Show warnings for deprecated fields during component initialization.
        """
        # call the parent constructor first to initialize Pydantic internals
        super().__init__(**model_fields)
        # set the placeholder for the default deprecation messages
        self._default_deprecation_messages: List[str] = []
        # set the placeholder for the deprecation logs
        self._deprecation_logs: List[ConnectorBuilderLogMessage] = []
        # process deprecated fields, if present
        self._process_fields(model_fields)
        # emit default deprecation messages
        self._emit_default_deprecation_messages()
        # set the deprecation logs attribute to the model
        self._set_deprecation_logs_attr_to_model()

    def _is_deprecated_field(self, field_name: str) -> bool:
        return (
            self.__fields__[field_name].field_info.extra.get(DEPRECATED, False)
            if field_name in self.__fields__.keys()
            else False
        )

    def _get_deprecation_message(self, field_name: str) -> str:
        return (
            self.__fields__[field_name].field_info.extra.get(
                DEPRECATION_MESSAGE, "<missing_deprecation_message>"
            )
            if field_name in self.__fields__.keys()
            else "<missing_deprecation_message>"
        )

    def _process_fields(self, model_fields: Any) -> None:
        """
        Processes the fields in the provided model data, checking for deprecated fields.

        For each field in the input `model_fields`, this method checks if the field exists in the model's defined fields.
        If the field is marked as deprecated (using the `DEPRECATED` flag in its metadata), it triggers a deprecation warning
        by calling the `_create_warning` method with the field name and an optional deprecation message.

        Args:
            model_fields (Any): The data containing fields to be processed.

        Returns:
            None
        """

        if hasattr(self, FIELDS_TAG):
            for field_name in model_fields.keys():
                if self._is_deprecated_field(field_name):
                    self._create_warning(
                        field_name,
                        self._get_deprecation_message(field_name),
                    )

    def _set_deprecation_logs_attr_to_model(self) -> None:
        """
        Sets the deprecation logs attribute on the model instance.

        This method attaches the current instance's deprecation logs to the model by setting
        an attribute named by `DEPRECATION_LOGS_TAG` to the value of `self._deprecation_logs`.
        This is typically used to track or log deprecated features or configurations within the model.

        Returns:
            None
        """
        setattr(self, DEPRECATION_LOGS_TAG, self._deprecation_logs)

    def _create_warning(self, field_name: str, message: str) -> None:
        """
        Show a warning message for deprecated fields (to stdout).
        Args:
            field_name (str): Name of the deprecated field.
            message (str): Warning message to be displayed.
        """

        deprecated_message = f"Component type: `{self.__class__.__name__}`. Field '{field_name}' is deprecated. {message}"

        if deprecated_message not in self._default_deprecation_messages:
            # Avoid duplicates in the default deprecation messages
            self._default_deprecation_messages.append(deprecated_message)

        # Create an Airbyte deprecation log message
        deprecation_log_message = ConnectorBuilderLogMessage(
            level="WARN", message=deprecated_message
        )
        # Add the deprecation message to the Airbyte log messages,
        # this logs are displayed in the Connector Builder.
        if deprecation_log_message not in self._deprecation_logs:
            # Avoid duplicates in the deprecation logs
            self._deprecation_logs.append(deprecation_log_message)

    def _emit_default_deprecation_messages(self) -> None:
        """
        Emit default deprecation messages for deprecated fields to STDOUT.
        """
        for message in self._default_deprecation_messages:
            warnings.warn(message, DeprecationWarning)
