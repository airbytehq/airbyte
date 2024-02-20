#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from source_smartsheets_2 import utils


class MockObject:
    """Object to mock sheets and folders."""
    def __init__(self, name):
        self.name = name


@pytest.mark.parametrize(
    ("sheets", "patterns"), [
        (
            [
                (MockObject("Foxtrot Golf Hotel v1.5"), ["/", "Alpha", "Beta", "Charlie Delta", "Echo"])
            ], ["/*/*beta*/*/*/*golf hotel*"]),
        (
            [
                (MockObject("Foxtrot Golf Hotel v1.5"), ["/", "Alpha", "Charlie Delta", "Echo"])
            ], ["/*/*/*/*golf hotel*"]
        ),
])
def test_sheet_inclusion(sheets, patterns):
    """Tests that the sheet inclusion logic matches sheets to correct patterns."""
    matched_sheets = utils.filter_sheets_by_inclusion(sheets, patterns)
    assert len(matched_sheets) == len(sheets)


@pytest.mark.parametrize(
    ("sheets", "patterns"), [
        (
            [
                (MockObject("Foxtrot Golf Hotel v1.5"), ["/", "Alpha", "Beta", "Charlie Delta", "Echo"])
                ], ["/*/*beta*/*/*/*indigo juliet*"]
        ),
        (
            [
                (MockObject("Foxtrot Golf Hotel v1.5"), ["/", "Alpha", "Charlie Delta", "Echo"])
            ], ["/*/*/*/*indigo juliet*"]
        ),
])
def test_sheet_exclusion(sheets, patterns):
    """Tests that the sheet inclusion logic does not match sheets to wrong patterns."""
    matched_sheets = utils.filter_sheets_by_inclusion(sheets, patterns)
    assert len(matched_sheets) == 0


@pytest.mark.parametrize(
    ("folders", "patterns"), [
        (
            [
                (MockObject("Charlie Delta"), ["/", "Alpha", "Beta"])
            ], ["/*/*/* delta*"]
        ),
        (
            [
                (MockObject("Echo"), ["/", "Alpha", "Beta", "Charlie Delta"])
            ], ["**/echo"]
        ),
])
def test_folder_inclusion(folders, patterns):
    """Tests that the folder inclusion logic matches folders to correct patterns."""
    matched_folders, unmatched_folders = utils.filter_folders_by_exclusion(folders, patterns)
    assert len(matched_folders) == len(folders)
    assert len(unmatched_folders) == 0


@pytest.mark.parametrize(
    ("folders", "patterns"), [
        (
            [
                (MockObject("Echo"), ["/", "Alpha", "Beta", "Charlie Delta"])
            ], ["/foxtrot"]
        ),
        (
            [
                (MockObject("Echo"), ["/", "Alpha", "Beta", "Charlie Delta"])
            ], ["**/foxtrot"]
        ),
])
def test_folder_exclusion(folders, patterns):
    """Tests that the folder exclusion logic does not match folders to wrong patterns."""
    matched_folders, unmatched_folders = utils.filter_folders_by_exclusion(folders, patterns)
    assert len(matched_folders) == 0
    assert len(unmatched_folders) == len(folders)
