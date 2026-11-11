# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from .object_response_builder import ObjectResponseBuilder


class ReportCheckStatusResponseBuilder(ObjectResponseBuilder):
    @classmethod
    def check_status_response(cls) -> "ReportCheckStatusResponseBuilder":
        return cls()
