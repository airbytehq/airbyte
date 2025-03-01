#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime


STRING_TYPES = [
    "string",
    "email",
    "reference",
    "url",
    "phone",
    "textarea",
    "text",
    "lead_function",
]


def to_datetime_str(date: datetime) -> str:
    """
    Returns the formated datetime string.
    :: Output example: '2021-07-15T0:0:0Z' FORMAT : "%Y-%m-%dT%H:%M:%SZ"
    """
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def clean_string(string: str) -> str:
    """
    input -> output
    "updatedAt" -> "updated_at"
    "UpdatedAt" -> "updated_at"
    "base URL" -> "base_url"
    "UPdatedAt" -> "u_pdated_at"
    "updated_at" -> "updated_at"
    " updated_at " -> "updated_at"
    "updatedat" -> "updatedat"
    "updated at" -> "updated_at"
    """

    fix = {
        "api method name": "Api Method Name",
        "modifying user": "Modifying User",
        "request id": "Request Id",
    }

    string = fix.get(string, string)
    abbreviations = ("URL", "GUID", "IP", "ID", "IDs", "API", "SFDC", "CRM", "SLA")
    if any(map(lambda w: w in string.split(), abbreviations)):
        return string.lower().replace(" ", "_")
    return "".join("_" + c.lower() if c.isupper() else c for c in string if c != " ").strip("_")


def format_value(value, schema):
    if not isinstance(schema["type"], list):
        field_type = [schema["type"]]
    else:
        field_type = schema["type"]

    if value in [None, "", "null"]:
        return None
    elif "integer" in field_type:
        if isinstance(value, int):
            return value

        # Custom Marketo percent type fields can have decimals, so we drop them
        decimal_index = value.find(".")
        if decimal_index > 0:
            value = value[:decimal_index]
        return int(value)
    elif "string" in field_type:
        return str(value)
    elif "number" in field_type:
        return float(value)
    elif "boolean" in field_type:
        if isinstance(value, bool):
            return value
        return value.lower() == "true"

    return value
