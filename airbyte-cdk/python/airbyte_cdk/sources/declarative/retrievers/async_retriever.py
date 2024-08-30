# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import InitVar, dataclass, field
from typing import Any, Callable, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.sources.declarative.async_job.job_orchestrator import AsyncJobOrchestrator
from airbyte_cdk.sources.declarative.extractors.record_selector import RecordSelector
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers import SinglePartitionRouter
from airbyte_cdk.sources.declarative.retrievers import Retriever
from airbyte_cdk.sources.declarative.stream_slicers import StreamSlicer
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_protocol.models import FailureType

_NO_NEXT_PAGE_TOKEN = None
_NO_STREAM_STATE = {}


@dataclass
class AsyncRetriever(Retriever):
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    job_orchestrator_factory: Callable[[Iterable[StreamSlice]], AsyncJobOrchestrator]
    record_selector: RecordSelector
    name: str
    _name: Union[InterpolatedString, str] = field(init=False, repr=False, default="")
    primary_key: Optional[Union[str, List[str], List[List[str]]]]
    _primary_key: str = field(init=False, repr=False, default="")
    stream_slicer: StreamSlicer = field(default_factory=lambda: SinglePartitionRouter(parameters={}))

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._job_orchestrator_factory = self.job_orchestrator_factory
        self.__job_orchestrator: Optional[AsyncJobOrchestrator] = None
        self._parameters = parameters
        self._name = InterpolatedString(self._name, parameters=parameters) if isinstance(self._name, str) else self._name

    @property  # type: ignore
    def name(self) -> str:
        """
        :return: Stream name
        """
        return str(self._name.eval(self.config)) if isinstance(self._name, InterpolatedString) else self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, property):
            self._name = value

    @property  # type: ignore
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """The stream's primary key"""
        return self._primary_key

    @primary_key.setter
    def primary_key(self, value: str) -> None:
        if not isinstance(value, property):
            self._primary_key = value

    @property
    def state(self) -> StreamState:
        """
        As a first iteration for sendgrid, there is no state to be managed
        """
        return {}

    @state.setter
    def state(self, value: StreamState) -> None:
        """
        As a first iteration for sendgrid, there is no state to be managed
        """
        pass

    @property
    def _job_orchestrator(self) -> AsyncJobOrchestrator:
        if self.__job_orchestrator:
            return self.__job_orchestrator

        raise AirbyteTracedException(
            message="Invalid state within AsyncJobRetriever. Please contact Airbyte Support",
            internal_message="AsyncPartitionRepository is expected to be accessed only after `stream_slices`",
            failure_type=FailureType.system_error,
        )

    def stream_slices(self) -> Iterable[Optional[StreamSlice]]:
        slices = self.stream_slicer.stream_slices()
        self.__job_orchestrator = self._job_orchestrator_factory(slices)

        for completed_partition in self._job_orchestrator.create_and_get_completed_partitions():
            yield StreamSlice(
                partition=dict(completed_partition.stream_slice.partition) | {"partition": completed_partition},
                cursor_slice=completed_partition.stream_slice.cursor_slice,
            )

    def read_records(
        self,
        records_schema: Mapping[str, Any],
        stream_slice: Optional[StreamSlice] = None,
    ) -> Iterable[StreamData]:
        if not isinstance(stream_slice, StreamSlice) or "partition" not in stream_slice.partition:
            raise AirbyteTracedException(
                message="Invalid arguments to AsyncJobRetriever.read_records: stream_slice is no optional. Please contact Airbyte Support",
                failure_type=FailureType.system_error,
            )

        yield from self.record_selector.filter_and_transform(
            self._job_orchestrator.fetch_records(stream_slice["partition"]),
            _NO_STREAM_STATE,
            records_schema,
            stream_slice,
            _NO_NEXT_PAGE_TOKEN,
        )
