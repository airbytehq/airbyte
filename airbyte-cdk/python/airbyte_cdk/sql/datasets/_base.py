# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any, cast

from pandas import DataFrame
from pyarrow.dataset import Dataset

from airbyte._util.document_rendering import DocumentRenderer
from airbyte.constants import DEFAULT_ARROW_MAX_CHUNK_SIZE


if TYPE_CHECKING:
    from pyarrow.dataset import Dataset

    from airbyte_protocol.models import ConfiguredAirbyteStream

    from airbyte.documents import Document


class DatasetBase(ABC):
    """Base implementation for all datasets."""

    def __init__(self, stream_metadata: ConfiguredAirbyteStream) -> None:
        self._stream_metadata = stream_metadata

    @abstractmethod
    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Return the iterator of records."""
        raise NotImplementedError

    def to_pandas(self) -> DataFrame:
        """Return a pandas DataFrame representation of the dataset.

        The base implementation simply passes the record iterator to Panda's DataFrame constructor.
        """
        # Technically, we return an iterator of Mapping objects. However, pandas
        # expects an iterator of dict objects. This cast is safe because we know
        # duck typing is correct for this use case.
        return DataFrame(cast(Iterator[dict[str, Any]], self))

    def to_arrow(
        self,
        *,
        max_chunk_size: int = DEFAULT_ARROW_MAX_CHUNK_SIZE,
    ) -> Dataset:
        """Return an Arrow Dataset representation of the dataset.

        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Not implemented in base class")

    def to_documents(
        self,
        title_property: str | None = None,
        content_properties: list[str] | None = None,
        metadata_properties: list[str] | None = None,
        *,
        render_metadata: bool = False,
    ) -> Iterable[Document]:
        """Return the iterator of documents.

        If metadata_properties is not set, all properties that are not content will be added to
        the metadata.

        If render_metadata is True, metadata will be rendered in the document, as well as the
        the main content. Otherwise, metadata will be attached to the document but not rendered.
        """
        renderer = DocumentRenderer(
            title_property=title_property,
            content_properties=content_properties,
            metadata_properties=metadata_properties,
            render_metadata=render_metadata,
        )
        yield from renderer.render_documents(self)
