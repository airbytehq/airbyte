#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


class ConfigValidationError(Exception):
    pass


class MissingSchemaError(Exception):
    pass


class RecordParseError(Exception):
    pass


class SchemaInferenceError(Exception):
    pass


class UndefinedParserError(Exception):
    pass
