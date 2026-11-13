# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from .object_response_builder import ObjectResponseBuilder


class ErrorResponseBuilder(ObjectResponseBuilder):
    @classmethod
    def non_breaking_error_response(cls) -> "ErrorResponseBuilder":
        return cls()

    @classmethod
    def breaking_error_response(cls) -> "ErrorResponseBuilder":
        return cls()
