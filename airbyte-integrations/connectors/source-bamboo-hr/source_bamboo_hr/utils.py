#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import List, Text, Dict


def convert_custom_reports_fields_to_list(custom_reports_fields: Text) -> List[Text]:
    """
    Converts a comma-delimited string into a list of stripped strings.
    """
    if custom_reports_fields is None:
        custom_reports_fields = ""
    custom_fields = [field.strip() for field in custom_reports_fields.split(",")]
    return custom_fields


def validate_custom_fields(custom_fields: List[Text], available_fields: List[Dict]) -> List[Text]:
    """
    Returns a list of custom fields which do not appear in the available fields.

    Each custom field is compared with both the `name` and `alias` of each available field;
    if no match is found in either of the two, the custom field is added to the list of denied fields.
    """
    denied_fields = []
    for custom_field in custom_fields:
        has_access_to_custom_field = any(
            custom_field in [
                available_field.get("name"),
                available_field.get("alias"),
            ] for available_field in available_fields
        )
        if not has_access_to_custom_field:
            denied_fields.append(custom_field)

    return denied_fields
