#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


# NETSUITTE REST API PATHS
REST_PATH: str = "/services/rest/"
RECORD_PATH: str = REST_PATH + "record/v1/"
META_PATH: str = RECORD_PATH + "metadata-catalog/"
SUITEQL_PATH: str = "/services/rest/query/v1/suiteql"

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


NETSUITE_INPUT_DATE_FORMATS: list[str] = ["%m/%d/%Y", "%Y-%m-%d"]
NETSUITE_OUTPUT_DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"

INVOICE_CLOSEDATE_SCHEMA: dict = {
  'type': 'object',
  'properties': {
    'closedate': {
      'title': 'Close Date',
      'type': 'string',
      'description': 'A close date',
      'format': 'date',
      'nullable': True
    },
    'duedate': {
      'title': 'Due Date',
      'type': 'string',
      'description': 'Type or pick the due date for this invoice. If you do not assign a due date, the due date defaults to the date in the Date field. In addition, if you do not assign a due date, this invoice will appear on aging reports.',
      'format': 'date',
      'nullable': True
    },
    'id': {
      'title': 'Internal ID',
      'type': 'string',
      'nullable': True
    },
  },
  '$schema': 'http://json-schema.org/draft-06/hyper-schema#',
  'x-ns-filterable': [
    'closedate',
    'duedate',
    'id'
  ]
}

SUITEQL_SCHEMAS: dict = {
    'invoice_closedate': INVOICE_CLOSEDATE_SCHEMA
}
