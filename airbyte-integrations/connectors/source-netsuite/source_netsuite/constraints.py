#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


# NETSUITTE REST API PATHS
REST_PATH: str = "/services/rest/"
RECORD_PATH: str = REST_PATH + "record/v1/"
META_PATH: str = RECORD_PATH + "metadata-catalog/"

# PREDEFINE REFERAL SCHEMA LINK, TEMPLATE
REFERAL_SCHEMA_URL: str = "/services/rest/record/v1/metadata-catalog/nsLink"
REFERAL_SCHEMA: dict = {
    "type": ["null", "object"],
    "properties": {
        "id": {"title": "Internal identifier", "type": ["string"]},
        "refName": {"title": "Reference Name", "type": ["null", "string"]},
        "externalId": {"title": "External identifier", "type": ["null", "string"]},
        "links": {
            "title": "Links",
            "type": "array",
            "readOnly": True,
        },
    },
}
# ELEMENTS TO REMOVE FROM SCHEMA
USLESS_SCHEMA_ELEMENTS: list = [
    "enum",
    "x-ns-filterable",
    "x-ns-custom-field",
    "nullable",
]

# PREDEFINE SCHEMA HEADER
SCHEMA_HEADERS: dict = {"Accept": "application/schema+json"}

# INCREMENTAL CURSOR FIELDS
INCREMENTAL_CURSOR: str = "lastModifiedDate"
CUSTOM_INCREMENTAL_CURSOR: str = "lastmodified"

# NETSUITE ERROR CODES BY THEIR HTTP TWINS
NETSUITE_ERRORS_MAPPING: dict = {
    400: {
        "USER_ERROR": "reading an Admin record allowed for Admin only",
        "NONEXISTENT_FIELD": "cursor_field declared in schema but doesn't exist in object",
        "INVALID_PARAMETER": "cannot read or find the object. Skipping",
    },
}
