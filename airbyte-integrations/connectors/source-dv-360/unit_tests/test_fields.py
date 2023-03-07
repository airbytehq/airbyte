#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_dv_360.fields import sanitize


def test_sanitize_with_pct():
    string = "% tesT string:"
    sanitized_string = sanitize(string)
    expected_result = "pct_test_string"

    assert sanitized_string == expected_result


def test_sanitize_trailing_space():
    string = "% tesT string:    "
    sanitized_string = sanitize(string)
    expected_result = "pct_test_string"

    assert sanitized_string == expected_result


def test_sanitize_leading_space():
    string = "  % tesT string:"
    sanitized_string = sanitize(string)
    expected_result = "pct_test_string"

    assert sanitized_string == expected_result


def test_sanitize_punctuation():
    string = "% tesT string:,;()#$"
    sanitized_string = sanitize(string)
    expected_result = "pct_test_string"

    assert sanitized_string == expected_result


def test_sanitize_slash():
    string = "% tesT string:/test"
    sanitized_string = sanitize(string)
    expected_result = "pct_test_string_test"

    assert sanitized_string == expected_result


def test_sanitize_and():
    string = "% tesT string & test"
    sanitized_string = sanitize(string)
    expected_result = "pct_test_string_and_test"

    assert sanitized_string == expected_result
