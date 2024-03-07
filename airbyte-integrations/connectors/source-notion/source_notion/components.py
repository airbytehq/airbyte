# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, MutableMapping

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.incremental import PerPartitionCursor

@dataclass
class NotionUserTransformation(RecordTransformation):
  """
  Custom transformation that conditionally moves the data in owner.{owner_type} 
  to a new owner.info field when the record contains data for a "bot" type user.
  """

  def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
    owner = record.get("bot", {}).get("owner")
    if owner:
      owner_type = owner.get("type")
      owner_info = owner.get(owner_type)
      if owner_type and owner_info:
        record["bot"]["owner"]["info"] = owner_info
        del record["bot"]["owner"][owner_type]
    return record


@dataclass
class NotionPropertiesTransformation(RecordTransformation):
  """
  Custom transformation that normalizes nested 'properties' object by moving
  unique named entities into 'name', 'value' mappings
  """

  def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
    properties = record.get("properties", {})
    transformed_properties = [
      {"name": name, "value": value} for name, value in properties.items()
    ]
    record["properties"] = transformed_properties
    return record


@dataclass
class NotionBlocksTransformation(RecordTransformation):
  """
  Transforms records containing 'mention' objects within their 'rich_text' fields. This method locates the 'mention'
  objects, extracts their type-specific information, and moves this information into a newly created 'info' field within
  the 'mention' object. It then removes the original type-specific field from the 'mention' object.

  The transformation specifically targets a field determined by the record's 'type' attribute. It iterates over each
  'mention' object within the 'rich_text' array of that field, restructures the 'mention' objects for consistency and
  easier access, and updates the record in-place.
  """

  def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
    transform_object_field = record.get("type")

    if transform_object_field:
      rich_text = record.get(transform_object_field, {}).get("rich_text", [])
      for r in rich_text:
        mention = r.get("mention")
        if mention:
          type_info = mention[mention["type"]]
          record[transform_object_field]["rich_text"][rich_text.index(r)]["mention"]["info"] = type_info
          del record[transform_object_field]["rich_text"][rich_text.index(r)]["mention"][mention["type"]]

    return record


@dataclass
class NotionSemiIncrementalPerPartitionCursor(PerPartitionCursor):
  pass
  
