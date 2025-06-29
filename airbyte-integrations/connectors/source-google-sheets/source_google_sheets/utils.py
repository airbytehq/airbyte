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


def safe_name_conversion(text: str) -> str:
    if not text:
        return text
    new = name_conversion(text)
    if not new:
        raise Exception(f"initial string '{text}' converted to empty")
    return new


def _sanitization(
    text: str,
    remove_leading_trailing_underscores: bool = False,
    combine_number_word_pairs: bool = False,
    remove_special_characters: bool = False,
    combine_letter_number_pairs: bool = False,
    allow_leading_numbers: bool = False,
) -> str:
    """
    Converts a string into a normalized, SQL-compliant name using a set of configurable options.

    Args:
        text: The input string to convert.
        remove_leading_trailing_underscores: If True, removes underscores at the start/end of the result.
        combine_number_word_pairs: If True, combines adjacent number and word tokens (e.g., "50 th" -> "50th").
        remove_special_characters: If True, removes all special characters from the input.
        combine_letter_number_pairs: If True, combines adjacent letter and number tokens (e.g., "Q 3" -> "Q3").
        allow_leading_numbers: If False, prepends an underscore if the result starts with a number.

    Returns:
        The normalized, SQL-compliant string.

    Steps:
    1. Transliterates the input text to ASCII using unidecode.
    2. Optionally removes special characters if remove_special_characters is True.
    3. Splits the text into tokens using a regex pattern that separates words, numbers, and non-alphanumeric characters.
    4. Optionally combines adjacent letter+number or number+word tokens based on flags.
    5. Removes empty tokens in the middle, but keeps leading/trailing empty tokens for underscore placement.
    6. Optionally strips leading/trailing underscores if remove_leading_trailing_underscores is True.
    7. Optionally prepends an underscore if the result starts with a number and allow_leading_numbers is False.
    8. Returns the final string in lowercase.
    """
    text = unidecode.unidecode(text)

    if remove_special_characters:
        text = re.sub(r"[^\w\s]", "", text)

    tokens = []
    for m in TOKEN_PATTERN.finditer(text):
        if m.group("NoToken") is None:
            tokens.append(m.group(0))
        else:
            tokens.append("")

    # Combine tokens as per flags
    combined_tokens = []
    i = 0
    while i < len(tokens):
        if (
            combine_letter_number_pairs
            and i + 1 < len(tokens)
            and tokens[i]
            and tokens[i].isalpha()
            and tokens[i + 1]
            and tokens[i + 1].isdigit()
        ):
            combined = tokens[i] + tokens[i + 1]
            combined_tokens.append(combined)
            i += 2
        elif (
            combine_number_word_pairs
            and i + 1 < len(tokens)
            and tokens[i]
            and tokens[i].isdigit()
            and tokens[i + 1]
            and tokens[i + 1].isalpha()
        ):
            combined = tokens[i] + tokens[i + 1]
            combined_tokens.append(combined)
            i += 2
        else:
            combined_tokens.append(tokens[i])
            i += 1

    # Find indices of first and last non-empty tokens
    first_non_empty = next((i for i, t in enumerate(combined_tokens) if t), len(combined_tokens))
    last_non_empty = next((i for i, t in reversed(list(enumerate(combined_tokens))) if t), -1)

    # Process tokens: keep leading/trailing empty tokens, remove empty tokens in middle
    if first_non_empty < len(combined_tokens):
        leading = combined_tokens[:first_non_empty]
        middle = [t for t in combined_tokens[first_non_empty : last_non_empty + 1] if t]
        trailing = combined_tokens[last_non_empty + 1 :]
        processed_tokens = leading + middle + trailing
    else:
        processed_tokens = combined_tokens  # All tokens are empty

    # Join tokens with underscores
    result = DEFAULT_SEPARATOR.join(processed_tokens)

    # Apply remove_leading_trailing_underscores on the final string
    if remove_leading_trailing_underscores:
        result = result.strip(DEFAULT_SEPARATOR)

    # Handle leading numbers after underscore removal
    if not allow_leading_numbers and result and result[0].isdigit():
        result = DEFAULT_SEPARATOR + result

    final_result = result.lower()
    return final_result


def safe_sanitzation_conversion(text: str, **kwargs) -> str:
    """
    Converts text to a safe name using _sanitization with the provided keyword arguments.
    Raises an exception if the result is empty or "_". Unlike safe_name_conversion,
    this function also rejects "_" as a valid result, since _sanitization
    may return "_" for certain inputs (e.g., "*").
    """
    new = _sanitization(text, **kwargs)
    if not new or new == "_":
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
