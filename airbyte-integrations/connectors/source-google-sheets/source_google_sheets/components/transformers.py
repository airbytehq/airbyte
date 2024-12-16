# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


# @dataclass
# class GoogleSheetRowsTransformation(RecordTransformation):
#     def __init__(self) -> None:
#         super().__init__()
#         self.schema_requester = resolve_manifest(source=SourceDynamicGoogleSheets(None, None, None)).record.data["manifest"]["dynamic_streams"][0]["stream_template"]["retriever"]["requester"]
#
#     def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
#         return record
