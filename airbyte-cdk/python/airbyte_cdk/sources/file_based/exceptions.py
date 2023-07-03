#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from enum import Enum


class FileBasedSourceError(Enum):
    EMPTY_STREAM = "No files were identified in the stream. This may be because there are no files in the specified container, or because your glob patterns did not match any files. Please verify that your source contains files and that your glob patterns are not overly strict."
    EXTENSION_MISMATCH = "The file type that you specified for this stream does not agree with the extension of one or more files in the stream. You may need to modify your glob patterns."
    GLOB_PARSE_ERROR = (
        "Error parsing glob pattern. Please refer to the glob pattern rules at https://facelessuser.github.io/wcmatch/glob/#split."
    )
    ERROR_LISTING_FILES = (
        "Error listing files. Please check the credentials provided in the config and verify that they provide permission to list files."
    )
    ERROR_READING_FILE = (
        "Error opening file. Please check the credentials provided in the config and verify that they provide permission to read files."
    )
    ERROR_PARSING_FILE = "Error parsing file. This could be due to a mismatch between the config's file type and the actual file type, or because the file is not parseable."
    ERROR_PARSING_USER_PROVIDED_SCHEMA = "The provided schema could not be transformed into valid JSON Schema."  # TODO
    ERROR_VALIDATING_RECORD = "One or more records do not pass the schema validation policy. Please modify your input schema, or select a more lenient validation policy."
    NULL_VALUE_IN_SCHEMA = "Error during schema inference: no type was detected for key."
    UNRECOGNIZED_TYPE = "Error during schema inference: unrecognized type."
    SCHEMA_INFERENCE_ERROR = "Error inferring schema for file. Is the file valid?"
    CONFIG_VALIDATION_ERROR = "Error creating stream config object."
    MISSING_SCHEMA = "Expected `json_schema` in the configured catalog but it is missing."
    UNDEFINED_PARSER = "No parser is defined for this file type."


class BaseFileBasedSourceError(Exception):
    def __init__(self, error: FileBasedSourceError, **kwargs):
        super().__init__(
            f"{FileBasedSourceError(error).value} Contact Support if you need assistance.\n{' '.join([f'{k}={v}' for k, v in kwargs.items()])}"
        )


class ConfigValidationError(BaseFileBasedSourceError):
    pass


class MissingSchemaError(BaseFileBasedSourceError):
    pass


class RecordParseError(BaseFileBasedSourceError):
    pass


class SchemaInferenceError(BaseFileBasedSourceError):
    pass


class CheckAvailabilityError(BaseFileBasedSourceError):
    pass


class UndefinedParserError(BaseFileBasedSourceError):
    pass
