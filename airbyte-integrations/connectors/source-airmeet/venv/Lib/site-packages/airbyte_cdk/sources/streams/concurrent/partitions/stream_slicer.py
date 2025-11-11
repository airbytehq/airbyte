# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Iterable

from airbyte_cdk.sources.types import StreamSlice


class StreamSlicerMeta(ABCMeta):
    """
    Metaclass for wrapper scenario that allows it to be used as a type check for StreamSlicer.
    This is necessary because StreamSlicerTestReadDecorator wraps a StreamSlicer and we want to be able to check
    if an instance is a StreamSlicer, even if it is wrapped in a StreamSlicerTestReadDecorator.

    For example in ConcurrentDeclarativeSource, we do things like:
        isinstance(declarative_stream.retriever.stream_slicer,(GlobalSubstreamCursor, PerPartitionWithGlobalCursor))
    """

    def __instancecheck__(cls, instance: Any) -> bool:
        # Check if it's our wrapper with matching wrapped class
        if hasattr(instance, "wrapped_slicer"):
            return isinstance(instance.wrapped_slicer, cls)

        return super().__instancecheck__(instance)


class StreamSlicer(ABC, metaclass=StreamSlicerMeta):
    """
    Slices the stream into chunks that can be fetched independently. Slices enable state checkpointing and data retrieval parallelization.
    """

    @abstractmethod
    def stream_slices(self) -> Iterable[StreamSlice]:
        """
        Defines stream slices

        :return: An iterable of stream slices
        """
        pass
