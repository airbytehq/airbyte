#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


# NETSUITE ERROR CODES BY THEIR HTTP TWINS
NETSUITE_ERRORS_MAPPING: dict = {
    400: {
        "USER_ERROR": "reading an Admin record allowed for Admin only",
        "NONEXISTENT_FIELD": "cursor_field declared in schema but doesn't exist in object",
        "INVALID_PARAMETER": "cannot read or find the object. Skipping",
    },
    403: {
        "INSUFFICIENT_PERMISSION": "not enough permissions to access the object",
    },
}


# NETSUITE API ERRORS EXCEPTIONS
class DateFormatExeption(Exception):
    """API CANNOT HANDLE REQUEST USING GIVEN DATETIME FORMAT"""
