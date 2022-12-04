#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from typing import Any, List, Mapping

Record = Mapping[str, Any]
# A FieldPointer designates a path to a field inside a mapping. For example, retrieving ["k1", "k1.2"] in the object {"k1" :{"k1.2":
# "hello"}] returns "hello"
FieldPointer = List[str]
Config = Mapping[str, Any]
ConnectionDefinition = Mapping[str, Any]
StreamSlice = Mapping[str, Any]
StreamState = Mapping[str, Any]
