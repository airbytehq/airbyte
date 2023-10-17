#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declare base / abstract models to be reused in a pipeline lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set

from anyio import Path
from connector_ops.utils import Connector
from pipelines.helpers.utils import METADATA_FILE_NAME


@dataclass(frozen=True)
class ConnectorWithModifiedFiles(Connector):
    modified_files: Set[Path] = field(default_factory=frozenset)

    @property
    def has_metadata_change(self) -> bool:
        return any(path.name == METADATA_FILE_NAME for path in self.modified_files)
