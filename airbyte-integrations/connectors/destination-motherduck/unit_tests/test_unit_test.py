# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
from destination_motherduck.destination import DestinationMotherDuck, UnicodeAwareNormalizer, validated_sql_name

from airbyte_cdk.sql._util.name_normalizers import LowerCaseNormalizer
from airbyte_cdk.sql.exceptions import AirbyteNameNormalizationError


def test_read_invalid_path():
    invalid_input = "/test.duckdb"
    with pytest.raises(ValueError):
        _ = DestinationMotherDuck._get_destination_path(invalid_input)

    assert True


@pytest.mark.parametrize(
    "input, expected",
    [
        ("test", "test"),
        ("test_123", "test_123"),
        ("test;123", None),
        ("test123;", None),
        ("test-123", None),
        ("test 123", None),
        ("test.123", None),
        ("test,123", None),
        ("test!123", None),
    ],
)
def test_validated_sql_name(input, expected):
    if expected is None:
        with pytest.raises(ValueError):
            validated_sql_name(input)
    else:
        assert validated_sql_name(input) == expected


class TestUnicodeAwareNormalizer:
    """Test the UnicodeAwareNormalizer that preserves Unicode characters."""

    def setup_method(self):
        self.normalizer = UnicodeAwareNormalizer()
        self.old_normalizer = LowerCaseNormalizer()

    @pytest.mark.parametrize(
        "input_name, expected_output",
        [
            # ASCII cases should behave like LowerCaseNormalizer
            ("normal_name", "normal_name"),
            ("Test Name", "test_name"),
            ("UPPERCASE", "uppercase"),
            ("Column With Spaces", "column_with_spaces"),
            ("mixed_123_name", "mixed_123_name"),
            ("123", "_123"),  # Digit prefix gets underscore
            ("test-with-dashes", "test_with_dashes"),
            ("test.with.dots", "test_with_dots"),
            ("test!@#$%^&*()", "test"),
            ("café", "café"),  # Should preserve Unicode letters
            # Unicode cases that should work (these fail with LowerCaseNormalizer)
            ("税率", "税率"),  # Japanese characters
            ("你好", "你好"),  # Chinese characters
            ("åäö", "åäö"),  # Nordic characters
            ("naïve", "naïve"),  # Accented characters
            ("Müller", "müller"),  # German umlauts
            ("Jürgen", "jürgen"),  # More German
            ("François", "françois"),  # French
            ("Москва", "москва"),  # Cyrillic (Russian)
            ("مرحبا", "مرحبا"),  # Arabic
            ("हिन्दी", "ह_न_द"),  # Hindi (complex script with combining chars)
            # Mixed Unicode and ASCII
            ("User 名前", "user_名前"),
            ("Product税率", "product税率"),
            ("Column_税率_Name", "column_税率_name"),
        ],
    )
    def test_unicode_aware_normalization(self, input_name, expected_output):
        """Test that UnicodeAwareNormalizer preserves Unicode while normalizing ASCII."""
        result = self.normalizer.normalize(input_name)
        assert result == expected_output

    def test_empty_name_raises_error(self):
        """Test that empty names raise appropriate error."""
        with pytest.raises(AirbyteNameNormalizationError) as exc_info:
            self.normalizer.normalize("")

        assert "Name cannot be empty after normalization" in str(exc_info.value)

    def test_whitespace_only_name_raises_error(self):
        """Test that whitespace-only names raise appropriate error."""
        with pytest.raises(AirbyteNameNormalizationError) as exc_info:
            self.normalizer.normalize("   ")

        assert "Name cannot be empty after normalization" in str(exc_info.value)

    def test_special_chars_only_raises_error(self):
        """Test that names with only special characters raise appropriate error."""
        with pytest.raises(AirbyteNameNormalizationError) as exc_info:
            self.normalizer.normalize("!@#$%^&*()")

        assert "Name cannot be empty after normalization" in str(exc_info.value)

    def test_ascii_compatibility_with_lowercase_normalizer(self):
        """Test that ASCII inputs produce the same results as LowerCaseNormalizer."""
        ascii_test_cases = [
            "normal_name",
            "Test Name",
            "UPPERCASE",
            "mixed_123_name",
            "Column With Spaces",
        ]

        for test_case in ascii_test_cases:
            try:
                old_result = self.old_normalizer.normalize(test_case)
                new_result = self.normalizer.normalize(test_case)
                assert new_result == old_result, f"ASCII compatibility failed for '{test_case}'"
            except AirbyteNameNormalizationError:
                # If old normalizer fails, new one should also fail
                with pytest.raises(AirbyteNameNormalizationError):
                    self.normalizer.normalize(test_case)

    def test_unicode_cases_that_fail_with_old_normalizer(self):
        """Test Unicode cases that fail with LowerCaseNormalizer but work with UnicodeAwareNormalizer."""
        unicode_test_cases = [
            ("税率", "税率"),  # The customer's specific problem case
            ("你好", "你好"),
            ("åäö", "åäö"),
        ]

        for input_name, expected in unicode_test_cases:
            # Old normalizer should fail
            with pytest.raises(AirbyteNameNormalizationError):
                self.old_normalizer.normalize(input_name)

            # New normalizer should succeed
            result = self.normalizer.normalize(input_name)
            assert result == expected

    def test_consecutive_underscores_collapsed(self):
        """Test that consecutive underscores are collapsed to single underscore."""
        result = self.normalizer.normalize("test___multiple___underscores")
        assert result == "test_multiple_underscores"

    def test_leading_trailing_underscores_removed(self):
        """Test that leading and trailing underscores are removed."""
        result = self.normalizer.normalize("___test___")
        assert result == "test"
