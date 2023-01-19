#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_jira.utils import safe_max


def test_safe_max_arg1_none():
    assert safe_max(None, 1) == 1


def test_safe_max_arg2_none():
    assert safe_max(1, None) == 1


def test_safe_max_both_args():
    assert safe_max(1, 2) == 2
