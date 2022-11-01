#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


def convert_custom_reports_fields_to_list(custom_reports_fields: str) -> list:
    return custom_reports_fields.split(",") if custom_reports_fields else []


def validate_custom_fields(custom_fields, available_fields):
    denied_fields = []
    for custom_field in custom_fields:
        has_access_to_custom_field = any(available_field.get("name") == custom_field for available_field in available_fields)
        if not has_access_to_custom_field:
            denied_fields.append(custom_field)

    return denied_fields
