# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import re
from pathlib import PurePath
from typing import Iterable, Optional

from smartsheet.models.enums import ColumnType
from smartsheet.models.folder import Folder
from smartsheet.models.sheet import Sheet


def filter_sheets_by_inclusion(sheets: Iterable[Sheet], patterns: Iterable[str]) -> list[tuple[Sheet, str]]:
    """
    Filters sheets by patterns if their canonical path matches any of the patterns. Matched sheets are included.

    :param sheets: Iterable of tuples of sheets and iterable of segments of the canonical path to the folder where the sheet resides.
    :param patterns: Iterable of case insensitive glob patterns.

    :return: List of tuples of sheets that matched a pattern and the pattern that they matched.
    """
    matched_sheets: list[Sheet] = []
    for sheet, folder_path in sheets:
        path = PurePath(*(segment.lower() for segment in folder_path), sheet.name.lower())
        for pattern in patterns:
            if path.match(pattern.lower()):
                matched_sheets.append((sheet, pattern))
                break
    return matched_sheets


def filter_folders_by_exclusion(
    folders: Iterable[tuple[Folder, Iterable[str]]], patterns: Iterable[str]
) -> tuple[list[Folder], list[tuple[Folder, str]]]:
    """
    Filter folders by patterns if their canonical path matches any of the patterns. Matched folders are excluded.

    :param folders: Iterable of tuples of folders and iterable of segments of the canonical path to the folder where the folder resides.
    :param patterns: Iterable of case insensitive glob patterns.

    :return: Tuple of list of unfiltered folders and list of tuple of filtered folders and the pattern that they matched.
    """
    unmatched_folders: list[Folder] = []
    matched_folders: list[tuple[Folder, str]] = []
    for folder, folder_path in folders:
        path = PurePath(*(segment.lower() for segment in folder_path), folder.name.lower())
        for pattern in patterns:
            if path.match(pattern.lower()):
                matched_folders.append((folder, pattern))
                break
        else:
            unmatched_folders.append(folder)
    return matched_folders, unmatched_folders


def convert_column_type(column_type: ColumnType) -> dict[str, str]:
    """
    Converts column type from Smartsheet conventions to Airbyte conventions.

    See:
    - https://help.smartsheet.com/articles/2480241-column-type-reference
    - https://smartsheet.github.io/smartsheet-python-sdk/smartsheet.models.enums.html#module-smartsheet.models.enums.column_type
    - https://docs.airbyte.com/understanding-airbyte/supported-data-types/#the-types

    :param column_type: Smartsheet style type.

    :return: A dictionary of Airbyte style type information.
    """
    mapping = {
        ColumnType.ABSTRACT_DATETIME: {"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"},
        ColumnType.CHECKBOX: {"type": "boolean"},
        ColumnType.CONTACT_LIST: {"type": "string"},
        ColumnType.DATE: {"type": "string", "format": "date"},
        ColumnType.DATETIME: {"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"},
        ColumnType.DURATION: {"type": "string"},
        # Our tests indicate that these types actually come across as 'TEXT_NUMBER' from the SDK
        # ColumnType.MULTI_CONTACT_LIST: {"type": "array", "items": {"type": "string"}},
        # ColumnType.MULTI_PICKLIST: {"type": "array", "items": {"type": "string"}},
        ColumnType.PICKLIST: {"type": "string"},
        ColumnType.PREDECESSOR: {"type": "string"},
        ColumnType.TEXT_NUMBER: {"type": "string"},
    }
    mapped_type = mapping.get(column_type, {"type": "string"})
    return mapped_type


def normalize_column_name(column: str, transformations: Optional[list[str]] = None) -> str:
    """
    Normalize a column name by applying the given transformations.

    Conflicts are resolved by applying only the first-in-list transformation.

    Transformations:
    - Make common substitutions: Apply sensible substitions for non-identifier characters, e.g. '%' to 'percent'.
    - Make all lower case: Converts all letters to lower case.
    - Make all upper case: Converts all letters to upper case, conflicts with 'Make all lower case'.
    - Strip whitespace: Removes all whitespace.
    - Trim outer whitespace: Removes only the beginning and the end whitespace, conflicts with 'Strip whitespace'.
    - Whitespace into underscores: Replaces continuous sections of whitespace characters with a single underscore, conflicts with 'Strip whitespace'.
    - Hyphens into underscores: Replaces continuous sections of whitespace characters with a single underscore.
    - Ensure starts with identifier character: Prepends an underscore if the first character is not in [a-zA-Z_]
    - Strip non-identifier characters: Removes all characters not in [A-Za-z0-9_].
    - Replace non-identifier characters with hex encoding: Replaces all characters not in [A-Za-z0-9_]

    :param column: Any string.
    "param transformations: An optional list of transformations from the connector spec.

    :return: String normalized by the given transformations.
    """
    # This function is not very nice, but I do not see a more elegant way at the moment.
    if transformations is None:
        transformations = []

    ret = column

    if "Make common substitutions" in transformations:
        # This is all we have for now
        ret = ret.replace("%", "Percent")

    if "Make all lower case" in transformations:
        ret = ret.lower()
    elif "Make all upper case" in transformations:
        ret = ret.upper()

    if "Strip whitespace" in transformations:
        ret = re.sub(r"\s+", "", ret)
    else:
        if "Trim outer whitespace" in transformations:
            ret = ret.strip()
        if "Whitespace into underscores" in transformations:
            ret = re.sub(r"\s+", "_", ret)

    if "Hyphens into underscores" in transformations:
        ret = re.sub(r"-+", "_", ret)

    if "Ensure starts with identifier character" in transformations:
        if not re.match(r"^[A-Za-z_]", ret):
            ret = f"_{ret}"

    if "Strip non-identifier characters" in transformations:
        ret = re.sub(r"[^A-Za-z0-9_]", "", ret)
    elif "Replace non-identifier characters with hex encoding" in transformations:
        ret = re.sub(r"[^A-Za-z0-9_]", lambda match: f"_x{ord(match.group(0)):x}", ret)

    return ret


def reconcile_types(left: ColumnType, right: ColumnType) -> ColumnType:
    """
    Compares two Airbyte style types to yield the least type that encompasses both.

    :param left: First type to compare.
    :param right: Second type to compare.

    :return: Least type that encompasses both input types.
    """
    # Expected common case
    if left == right:
        return left

    equivalence_classes = [
        {ColumnType.ABSTRACT_DATETIME},
        {ColumnType.CHECKBOX},
        {ColumnType.CONTACT_LIST, ColumnType.DURATION, ColumnType.PICKLIST, ColumnType.PREDECESSOR, ColumnType.TEXT_NUMBER},
        {ColumnType.DATE},
        {ColumnType.DATETIME},
        # Our tests indicate that these types actually come across as 'TEXT_NUMBER' from the SDK
        # {ColumnType.MULTI_CONTACT_LIST, ColumnType.MULTI_PICKLIST},
    ]

    left_class_idx = next((cls for cls in equivalence_classes if left in cls), None)
    right_class_idx = next((cls for cls in equivalence_classes if right in cls), None)

    # In case future updates create new types
    assert left_class_idx is not None and right_class_idx is not None, "Schema sheet contains unrecognized type: '%s' or '%s'" % (
        left,
        right,
    )

    # Equivalent types, return any of them
    if left_class_idx == right_class_idx:
        return left

    # TEXT_NUMBER is the universal type
    return ColumnType.TEXT_NUMBER
