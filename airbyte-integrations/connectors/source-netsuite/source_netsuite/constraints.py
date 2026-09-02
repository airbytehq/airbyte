#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
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


# Record collection filtering runs on NetSuite's N/query module, whose `q` parameter accepts
# only bare date literals rendered in the account's date-format preference. Datetime literals
# are rejected there, including ISO-8601 -- see the comment on MAX_NETSUITE_UTC_OFFSET_HOURS.
NETSUITE_INPUT_DATE_FORMATS: list[str] = ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y"]
NETSUITE_OUTPUT_DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"

# Timezone-neutral representation carried on stream slices. Slice bounds are rendered into
# whichever `NETSUITE_INPUT_DATE_FORMATS` entry the account accepts at request time, so a
# date-format fallback can re-issue the same slice under the next candidate format.
SLICE_DATE_FORMAT: str = "%Y-%m-%d"

# NetSuite resolves the bare date literals in a `q` filter in the *account's* configured
# timezone, not UTC. On an account behind UTC, `AFTER "03/15/2026"` therefore means
# 2026-03-15T07:00:00Z (US Pacific), not midnight UTC -- so truncating the cursor to its own
# date asks for records after a moment that is *later* than the cursor, and everything modified
# in between is never requested by any sync. Shifting the cursor back by the largest negative
# UTC offset NetSuite offers (UTC-12) before truncating guarantees the queried window opens at
# or before the cursor instant on every account, whatever its timezone.
MAX_NETSUITE_UTC_OFFSET_HOURS: int = 12
