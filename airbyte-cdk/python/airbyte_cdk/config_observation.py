#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import (  # Used to evaluate type hints at runtime, a NameError: name 'ConfigObserver' is not defined is thrown otherwise
    annotations,
)

import time
from copy import copy
from typing import Any, List, MutableMapping

from airbyte_cdk.models import (
    AirbyteControlConnectorConfigMessage,
    AirbyteControlMessage,
    AirbyteMessage,
    AirbyteMessageSerializer,
    OrchestratorType,
    Type,
)
from orjson import orjson


class ObservedDict(dict):  # type: ignore # disallow_any_generics is set to True, and dict is equivalent to dict[Any]
    def __init__(
        self, non_observed_mapping: MutableMapping[Any, Any], observer: ConfigObserver, update_on_unchanged_value: bool = True
    ) -> None:
        non_observed_mapping = copy(non_observed_mapping)
        self.observer = observer
        self.update_on_unchanged_value = update_on_unchanged_value
        for item, value in non_observed_mapping.items():
            # Observe nested dicts
            if isinstance(value, MutableMapping):
                non_observed_mapping[item] = ObservedDict(value, observer)

            # Observe nested list of dicts
            if isinstance(value, List):
                for i, sub_value in enumerate(value):
                    if isinstance(sub_value, MutableMapping):
                        value[i] = ObservedDict(sub_value, observer)
        super().__init__(non_observed_mapping)

    def __setitem__(self, item: Any, value: Any) -> None:
        """Override dict.__setitem__ by:
        1. Observing the new value if it is a dict
        2. Call observer update if the new value is different from the previous one
        """
        previous_value = self.get(item)
        if isinstance(value, MutableMapping):
            value = ObservedDict(value, self.observer)
        if isinstance(value, List):
            for i, sub_value in enumerate(value):
                if isinstance(sub_value, MutableMapping):
                    value[i] = ObservedDict(sub_value, self.observer)
        super(ObservedDict, self).__setitem__(item, value)
        if self.update_on_unchanged_value or value != previous_value:
            self.observer.update()


class ConfigObserver:
    """This class is made to track mutations on ObservedDict config.
    When update is called a CONNECTOR_CONFIG control message is emitted on stdout.
    """

    def set_config(self, config: ObservedDict) -> None:
        self.config = config

    def update(self) -> None:
        emit_configuration_as_airbyte_control_message(self.config)


def observe_connector_config(non_observed_connector_config: MutableMapping[str, Any]) -> ObservedDict:
    if isinstance(non_observed_connector_config, ObservedDict):
        raise ValueError("This connector configuration is already observed")
    connector_config_observer = ConfigObserver()
    observed_connector_config = ObservedDict(non_observed_connector_config, connector_config_observer)
    connector_config_observer.set_config(observed_connector_config)
    return observed_connector_config


def emit_configuration_as_airbyte_control_message(config: MutableMapping[str, Any]) -> None:
    """
    WARNING: deprecated - emit_configuration_as_airbyte_control_message is being deprecated in favor of the MessageRepository mechanism.
    See the airbyte_cdk.sources.message package
    """
    airbyte_message = create_connector_config_control_message(config)
    print(orjson.dumps(AirbyteMessageSerializer.dump(airbyte_message)).decode())


def create_connector_config_control_message(config: MutableMapping[str, Any]) -> AirbyteMessage:
    control_message = AirbyteControlMessage(
        type=OrchestratorType.CONNECTOR_CONFIG,
        emitted_at=time.time() * 1000,
        connectorConfig=AirbyteControlConnectorConfigMessage(config=config),
    )
    return AirbyteMessage(type=Type.CONTROL, control=control_message)
