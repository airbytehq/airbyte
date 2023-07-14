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
    ERROR_CASTING_VALUE = "Could not cast the value to the expected type."
    ERROR_CASTING_VALUE_UNRECOGNIZED_TYPE = "Could not cast the value to the expected type because the type is not recognized. Valid types are null, array, boolean, integer, number, object, and string."
    ERROR_DECODING_VALUE = "Expected a JSON-decodeable value but could not decode record."
    ERROR_LISTING_FILES = (
        "Error listing files. Please check the credentials provided in the config and verify that they provide permission to list files."
    )
    ERROR_READING_FILE = (
        "Error opening file. Please check the credentials provided in the config and verify that they provide permission to read files."
    )
    ERROR_PARSING_RECORD = "Error parsing record. This could be due to a mismatch between the config's file type and the actual file type, or because the file or record is not parseable."
    ERROR_PARSING_USER_PROVIDED_SCHEMA = "The provided schema could not be transformed into valid JSON Schema."
    ERROR_VALIDATING_RECORD = "One or more records do not pass the schema validation policy. Please modify your input schema, or select a more lenient validation policy."
    STOP_SYNC_PER_SCHEMA_VALIDATION_POLICY = (
        "Stopping sync in accordance with the configured validation policy. Records in file did not conform to the schema."
    )
    NULL_VALUE_IN_SCHEMA = "Error during schema inference: no type was detected for key."
    UNRECOGNIZED_TYPE = "Error during schema inference: unrecognized type."
    SCHEMA_INFERENCE_ERROR = "Error inferring schema from files. Are the files valid?"
    INVALID_SCHEMA_ERROR = "No fields were identified for this schema. This may happen if the stream is empty. Please check your configuration to verify that there are files that match the stream's glob patterns."
    CONFIG_VALIDATION_ERROR = "Error creating stream config object."
    MISSING_SCHEMA = "Expected `json_schema` in the configured catalog but it is missing."
    UNDEFINED_PARSER = "No parser is defined for this file type."
    UNDEFINED_VALIDATION_POLICY = "The validation policy defined in the config does not exist for the source."


class BaseFileBasedSourceError(Exception):
    def __init__(self, error: FileBasedSourceError, **kwargs):  # type: ignore # noqa
        super().__init__(
            f"{FileBasedSourceError(error).value} Contact Support if you need assistance.\n{' '.join([f'{k}={v}' for k, v in kwargs.items()])}"
        )


class ConfigValidationError(BaseFileBasedSourceError):
    pass


class InvalidSchemaError(BaseFileBasedSourceError):
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


class StopSyncPerValidationPolicy(BaseFileBasedSourceError):
    pass
