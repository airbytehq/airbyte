# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from .object_response_builder import ObjectResponseBuilder


class ReportInitResponseBuilder(ObjectResponseBuilder):
    @classmethod
    def report_init_response(cls) -> "ReportInitResponseBuilder":
        return cls()
