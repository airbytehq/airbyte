#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import re

import unidecode
from requests.status_codes import codes as status_codes


TOKEN_PATTERN = re.compile(r"[A-Z]+[a-z]*|[a-z]+|\d+|(?P<NoToken>[^a-zA-Z\d]+)")
DEFAULT_SEPARATOR = "_"


def name_conversion(text: str) -> str:
    """
    convert name using a set of rules, for example: '1MyName' -> '_1_my_name'
    """
    text = unidecode.unidecode(text)

    tokens = []
    for m in TOKEN_PATTERN.finditer(text):
        if m.group("NoToken") is None:
            tokens.append(m.group(0))
        else:
            tokens.append("")

    if len(tokens) >= 3:
        tokens = tokens[:1] + [t for t in tokens[1:-1] if t] + tokens[-1:]

    if tokens and tokens[0].isdigit():
        tokens.insert(0, "")

    text = DEFAULT_SEPARATOR.join(tokens)
    text = text.lower()
    return text


def experimental_name_conversion(text: str) -> str:
    """
    Convert name using a set of rules, for example: '1MyName' -> '_1_my_name'
    Removes leading/trailing spaces and combines number-word pairs (e.g., '50th' -> '50th').
    """
    text = unidecode.unidecode(text.strip())  # Strip leading/trailing spaces

    tokens = []
    for m in TOKEN_PATTERN.finditer(text):
        if m.group("NoToken") is None:
            tokens.append(m.group(0))
        else:
            tokens.append("")

    # Combine number followed by word (e.g., "50" and "th" -> "50th")
    combined_tokens = []
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens) and tokens[i].isdigit() and tokens[i + 1].isalpha():
            combined_tokens.append(tokens[i] + tokens[i + 1])
            i += 2
        else:
            combined_tokens.append(tokens[i])
            i += 1

    if len(combined_tokens) >= 3:
        combined_tokens = combined_tokens[:1] + [t for t in combined_tokens[1:-1] if t] + combined_tokens[-1:]

    if combined_tokens and combined_tokens[0].isdigit():
        combined_tokens.insert(0, "")

    text = DEFAULT_SEPARATOR.join(combined_tokens)
    text = text.lower()
    return text


def safe_name_conversion(text: str) -> str:
    if not text:
        return text
    new = name_conversion(text)
    if not new:
        raise Exception(f"initial string '{text}' converted to empty")
    return new


def experimental_safe_name_conversion(text: str) -> str:
    if not text:
        return text
    new = experimental_name_conversion(text)
    if not new:
        raise Exception(f"initial string '{text}' converted to empty")
    return new


def exception_description_by_status_code(code: int, spreadsheet_id) -> str:
    if code in [status_codes.INTERNAL_SERVER_ERROR, status_codes.BAD_GATEWAY, status_codes.SERVICE_UNAVAILABLE]:
        return (
            "There was an issue with the Google Sheets API. This is usually a temporary issue from Google's side."
            " Please try again. If this issue persists, contact support"
        )
    if code == status_codes.FORBIDDEN:
        return (
            f"The authenticated Google Sheets user does not have permissions to view the spreadsheet with id {spreadsheet_id}. "
            "Please ensure the authenticated user has access to the Spreadsheet and reauthenticate. If the issue persists, contact support"
        )
    if code == status_codes.NOT_FOUND:
        return (
            f"The requested Google Sheets spreadsheet with id {spreadsheet_id} does not exist. "
            f"Please ensure the Spreadsheet Link you have set is valid and the spreadsheet exists. If the issue persists, contact support"
        )

    if code == status_codes.TOO_MANY_REQUESTS:
        return "Rate limit has been reached. Please try later or request a higher quota for your account."

    return ""
