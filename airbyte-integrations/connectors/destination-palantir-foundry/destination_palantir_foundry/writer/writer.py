from abc import ABC, abstractmethod

from airbyte_cdk.models.airbyte_protocol import ConfiguredAirbyteStream, AirbyteRecordMessage


class Writer(ABC):
    """
    Register a message stream if one doesn't exist.
    """

    @abstractmethod
    def ensure_registered(self, airbyte_stream: ConfiguredAirbyteStream):
        pass

    """
    Add a row to the writer output
    """

    @abstractmethod
    def add_record(self, airbyte_record: AirbyteRecordMessage):
        pass

    """
    Ensure that all records for the stream have been written to Foundry.
    """

    @abstractmethod
    def ensure_flushed(self, namespace: str, stream_name: str):
        pass
