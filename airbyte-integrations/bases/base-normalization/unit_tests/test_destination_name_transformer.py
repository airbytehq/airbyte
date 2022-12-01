#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import os

import pytest
from normalization.destination_type import DestinationType
from normalization.transform_catalog.destination_name_transformer import (
    DestinationNameTransformer,
    strip_accents,
    transform_standard_naming,
)


@pytest.fixture(scope="function", autouse=True)
def before_tests(request):
    # This makes the test run whether it is executed from the tests folder (with pytest/gradle)
    # or from the base-normalization folder (through pycharm)
    unit_tests_dir = os.path.join(request.fspath.dirname, "unit_tests")
    if os.path.exists(unit_tests_dir):
        os.chdir(unit_tests_dir)
    else:
        os.chdir(request.fspath.dirname)
    yield
    os.chdir(request.config.invocation_dir)


@pytest.mark.parametrize(
    "input_str, destination_type, expected",
    [
        # Contains Space character
        ("Hello World", "Postgres", True),
        ("Hello World", "BigQuery", False),
        ("Hello World", "Snowflake", True),
        ("Hello World", "Redshift", True),
        ("Hello World", "MySQL", True),
        ("Hello World", "MSSQL", True),
        ("Hello World", "TiDB", True),
        # Reserved Word for BigQuery and MySQL only
        ("Groups", "Postgres", False),
        ("Groups", "BigQuery", True),
        ("Groups", "Snowflake", False),
        ("Groups", "Redshift", False),
        ("Groups", "MySQL", True),
        ("Groups", "MSSQL", False),
        ("Groups", "TiDB", True),
        # Doesnt start with alpha or underscore
        ("100x200", "Postgres", True),
        ("100x200", "BigQuery", False),
        ("100x200", "Snowflake", True),
        ("100x200", "Redshift", True),
        ("100x200", "MySQL", True),
        ("100x200", "MSSQL", True),
        ("100x200", "TiDB", True),
        # Contains non alpha numeric
        ("post.wall", "Postgres", True),
        ("post.wall", "BigQuery", False),
        ("post.wall", "Snowflake", True),
        ("post.wall", "Redshift", True),
        ("post.wall", "MySQL", True),
        ("post.wall", "MSSQL", True),
        ("post.wall", "TiDB", True),
    ],
)
def test_needs_quote(input_str: str, destination_type: str, expected: bool):
    name_transformer = DestinationNameTransformer(DestinationType.from_string(destination_type))
    assert name_transformer.needs_quotes(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("Hello World!", "Hello World!"),
        ("àêî öÙ", "aei oU"),
    ],
)
def test_strip_accents(input_str: str, expected: str):
    assert strip_accents(input_str) == expected


@pytest.mark.parametrize(
    "expected, input_str",
    [
        ("__identifier_name", "__identifier_name"),
        ("IDENTIFIER_NAME", "IDENTIFIER_NAME"),
        ("123identifier_name", "123identifier_name"),
        ("i0d0e0n0t0i0f0i0e0r0n0a0m0e", "i0d0e0n0t0i0f0i0e0r0n0a0m0e"),
        ("_identifier_name", ",identifier+name"),
        ("identifier_name", "identifiêr name"),
        ("a_unicode_name__", "a_unicode_name_文"),
        ("identifier__name__", "identifier__name__"),
        ("identifier_name_weee", "identifier-name.weee"),
        ("_identifier_name_", '"identifier name"'),
        ("identifier_name", "identifier name"),
        ("identifier_", "identifier%"),
        ("_identifier_", "`identifier`"),
    ],
)
def test_transform_standard_naming(input_str: str, expected: str):
    assert transform_standard_naming(input_str) == expected


@pytest.mark.parametrize(
    "input_str, destination_type, expected, expected_in_jinja",
    [
        # Case sensitive names
        ("Identifier Name", "Postgres", "{{ adapter.quote('Identifier Name') }}", "adapter.quote('Identifier Name')"),
        ("Identifier Name", "BigQuery", "Identifier_Name", "'Identifier_Name'"),
        ("Identifier Name", "Snowflake", "{{ adapter.quote('Identifier Name') }}", "adapter.quote('Identifier Name')"),
        ("Identifier Name", "Redshift", "{{ adapter.quote('identifier name') }}", "adapter.quote('identifier name')"),
        ("Identifier Name", "MySQL", "{{ adapter.quote('Identifier Name') }}", "adapter.quote('Identifier Name')"),
        ("Identifier Name", "MSSQL", "{{ adapter.quote('Identifier Name') }}", "adapter.quote('Identifier Name')"),
        ("Identifier Name", "TiDB", "{{ adapter.quote('Identifier Name') }}", "adapter.quote('Identifier Name')"),
        # Reserved Word for BigQuery and MySQL only
        ("Groups", "Postgres", "groups", "'groups'"),
        ("Groups", "BigQuery", "{{ adapter.quote('Groups') }}", "adapter.quote('Groups')"),
        ("Groups", "Snowflake", "GROUPS", "'GROUPS'"),
        ("Groups", "Redshift", "groups", "'groups'"),
        ("Groups", "MySQL", "{{ adapter.quote('Groups') }}", "adapter.quote('Groups')"),
        ("Groups", "MSSQL", "groups", "'groups'"),
        ("Groups", "TiDB", "{{ adapter.quote('Groups') }}", "adapter.quote('Groups')"),
    ],
)
def test_normalize_column_name(input_str: str, destination_type: str, expected: str, expected_in_jinja: str):
    t = DestinationType.from_string(destination_type)
    assert DestinationNameTransformer(t).normalize_column_name(input_str, in_jinja=False) == expected
    assert DestinationNameTransformer(t).normalize_column_name(input_str, in_jinja=True) == expected_in_jinja


@pytest.mark.parametrize(
    "input_str, expected",
    [
        # below the limit
        ("Aaaa_Bbbb_Cccc_Dddd_Eeee_Ffff_Gggg_Hhhh", "Aaaa_Bbbb_Cccc_Dddd_Eeee_Ffff_Gggg_Hhhh"),
        # at the limit
        ("Aaaa_Bbbb_Cccc_Dddd_Eeee_Ffff_Gggg_Hhhh_Iii", "Aaaa_Bbbb_Cccc_Dddd_Eeee_Ffff_Gggg_Hhhh_Iii"),
        # over the limit
        ("Aaaa_Bbbb_Cccc_Dddd_Eeee_Ffff_Gggg_Hhhh_Iiii", "Aaaa_Bbbb_Cccc_Dddd___e_Ffff_Gggg_Hhhh_Iiii"),
        ("Aaaa_Bbbb_Cccc_Dddd_Eeee_a_very_long_name_Ffff_Gggg_Hhhh_Iiii", "Aaaa_Bbbb_Cccc_Dddd___e_Ffff_Gggg_Hhhh_Iiii"),
        ("Aaaa_Bbbb_Cccc_Dddd_Eeee_Ffff_Gggg_Hhhh_Iiii_Jjjj_Kkkk", "Aaaa_Bbbb_Cccc_Dddd___g_Hhhh_Iiii_Jjjj_Kkkk"),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz_0123456789", "ABCDEFGHIJKLMNOPQRST__qrstuvwxyz_0123456789"),
    ],
)
def test_truncate_identifier(input_str: str, expected: str):
    """
    Rules about truncations, for example for both of these strings which are too long for the postgres 64 limit:
    - `Aaaa_Bbbb_Cccc_Dddd_Eeee_Ffff_Gggg_Hhhh_Iiii`
    - `Aaaa_Bbbb_Cccc_Dddd_Eeee_a_very_long_name_Ffff_Gggg_Hhhh_Iiii`

    Deciding on how to truncate (in the middle) are being verified in these tests.
    In this instance, both strings ends up as:`Aaaa_Bbbb_Cccc_Dddd___e_Ffff_Gggg_Hhhh_Iiii`
    and can potentially cause a collision in table names.

    Note that dealing with such collisions is not part of `destination_name_transformer` but of the `stream_processor`.
    """
    name_transformer = DestinationNameTransformer(DestinationType.POSTGRES)
    print(f"Truncating from #{len(input_str)} to #{len(expected)}")
    assert name_transformer.truncate_identifier_name(input_str) == expected


@pytest.mark.parametrize(
    "input_str, destination_type, expected, expected_column",
    [
        # Case sensitive names
        ("Identifier Name1", "Postgres", "identifier_name1", "{{ adapter.quote('Identifier Name1') }}"),
        ("Identifier Name2", "BigQuery", "Identifier_Name2", "Identifier_Name2"),
        ("Identifier Name3", "Snowflake", "IDENTIFIER_NAME3", "{{ adapter.quote('Identifier Name3') }}"),
        ("Identifier Name4", "Redshift", "identifier_name4", "{{ adapter.quote('identifier name4') }}"),
        ("Identifier Name5", "MySQL", "identifier_name5", "{{ adapter.quote('Identifier Name5') }}"),
        ("Identifier Name6", "MSSQL", "identifier_name6", "{{ adapter.quote('Identifier Name6') }}"),
        ("Identifier Name7", "TiDB", "identifier_name7", "{{ adapter.quote('Identifier Name7') }}"),
        # Unicode
        ("a-Unicode_name_文1", "Postgres", "a_unicode_name__1", "{{ adapter.quote('a-Unicode_name_文1') }}"),
        ("a-Unicode_name_文2", "BigQuery", "a_Unicode_name__2", "a_Unicode_name__2"),
        ("a-Unicode_name_文3", "Snowflake", "A_UNICODE_NAME__3", "{{ adapter.quote('a-Unicode_name_文3') }}"),
        ("a-Unicode_name_文4", "Redshift", "a_unicode_name__4", "{{ adapter.quote('a-unicode_name_文4') }}"),
        ("a-Unicode_name_文5", "MySQL", "a_unicode_name__5", "{{ adapter.quote('a-Unicode_name_文5') }}"),
        ("a-Unicode_name_文6", "MSSQL", "a_unicode_name__6", "{{ adapter.quote('a-Unicode_name_文6') }}"),
        ("a-Unicode_name_文7", "TiDB", "a_unicode_name__7", "{{ adapter.quote('a-Unicode_name_文7') }}"),
        # Doesnt start with alpha or underscore
        ("100x2001", "Postgres", "100x2001", "{{ adapter.quote('100x2001') }}"),
        ("100x2002", "BigQuery", "100x2002", "_100x2002"),
        ("文2_a-Unicode_name", "BigQuery", "_2_a_Unicode_name", "_2_a_Unicode_name"),
        ("100x2003", "Snowflake", "100x2003", "{{ adapter.quote('100x2003') }}"),
        ("100x2004", "Redshift", "100x2004", "{{ adapter.quote('100x2004') }}"),
        ("100x2005", "MySQL", "100x2005", "{{ adapter.quote('100x2005') }}"),
        ("100x2006", "MSSQL", "_100x2006", "{{ adapter.quote('100x2006') }}"),
        ("100x2007", "TiDB", "100x2007", "{{ adapter.quote('100x2007') }}"),
        # Reserved Keywords in BQ and MySQL
        ("Groups", "Postgres", "groups", "groups"),
        ("Groups", "BigQuery", "Groups", "{{ adapter.quote('Groups') }}"),
        ("Groups", "Snowflake", "GROUPS", "GROUPS"),
        ("Groups", "Redshift", "groups", "groups"),
        ("Groups", "MySQL", "Groups", "{{ adapter.quote('Groups') }}"),
        ("Groups", "MSSQL", "groups", "groups"),
        ("Groups", "TiDB", "Groups", "{{ adapter.quote('Groups') }}"),
        # Reserved Keywords
        ("DisTincT", "Postgres", "DisTincT", "{{ adapter.quote('DisTincT') }}"),
        ("DisTincT", "BigQuery", "DisTincT", "{{ adapter.quote('DisTincT') }}"),
        ("DisTincT", "Snowflake", "DisTincT", "{{ adapter.quote('DisTincT') }}"),
        ("DisTincT", "Redshift", "distinct", "{{ adapter.quote('distinct') }}"),
        ("DisTincT", "MySQL", "DisTincT", "{{ adapter.quote('DisTincT') }}"),
        ("DisTincT", "MSSQL", "DisTincT", "{{ adapter.quote('DisTincT') }}"),
        ("DisTincT", "TiDB", "DisTincT", "{{ adapter.quote('DisTincT') }}"),
        # Quoted identifiers
        ("'QuoTed1 IdenTifiER'", "Postgres", "_quoted1_identifier_", "{{ adapter.quote('\\'QuoTed1 IdenTifiER\\'') }}"),
        ("'QuoTed2 IdenTifiER'", "BigQuery", "_QuoTed2_IdenTifiER_", "_QuoTed2_IdenTifiER_"),
        ("'QuoTed3 IdenTifiER'", "Snowflake", "_QUOTED3_IDENTIFIER_", "{{ adapter.quote('\\'QuoTed3 IdenTifiER\\'') }}"),
        ("'QuoTed4 IdenTifiER'", "Redshift", "_quoted4_identifier_", "{{ adapter.quote('\\'quoted4 identifier\\'') }}"),
        ("'QuoTed5 IdenTifiER'", "MySQL", "_quoted5_identifier_", "{{ adapter.quote('\\'QuoTed5 IdenTifiER\\'') }}"),
        ("'QuoTed6 IdenTifiER'", "MSSQL", "_quoted6_identifier_", "{{ adapter.quote('\\'QuoTed6 IdenTifiER\\'') }}"),
        ("'QuoTed7 IdenTifiER'", "TiDB", "_quoted7_identifier_", "{{ adapter.quote('\\'QuoTed7 IdenTifiER\\'') }}"),
        # Double Quoted identifiers
        ('"QuoTed7 IdenTifiER"', "Postgres", "_quoted7_identifier_", '{{ adapter.quote(\'""QuoTed7 IdenTifiER""\') }}'),
        ('"QuoTed8 IdenTifiER"', "BigQuery", "_QuoTed8_IdenTifiER_", "_QuoTed8_IdenTifiER_"),
        ('"QuoTed9 IdenTifiER"', "Snowflake", "_QUOTED9_IDENTIFIER_", '{{ adapter.quote(\'""QuoTed9 IdenTifiER""\') }}'),
        ('"QuoTed10 IdenTifiER"', "Redshift", "_quoted10_identifier_", '{{ adapter.quote(\'""quoted10 identifier""\') }}'),
        ('"QuoTed11 IdenTifiER"', "MySQL", "_quoted11_identifier_", "{{ adapter.quote('\"QuoTed11 IdenTifiER\"') }}"),
        ('"QuoTed12 IdenTifiER"', "MSSQL", "_quoted12_identifier_", '{{ adapter.quote(\'""QuoTed12 IdenTifiER""\') }}'),
        ('"QuoTed13 IdenTifiER"', "TiDB", "_quoted13_identifier_", "{{ adapter.quote('\"QuoTed13 IdenTifiER\"') }}"),
        # Back Quoted identifiers
        ("`QuoTed13 IdenTifiER`", "Postgres", "_quoted13_identifier_", "{{ adapter.quote('`QuoTed13 IdenTifiER`') }}"),
        ("`QuoTed14 IdenTifiER`", "BigQuery", "_QuoTed14_IdenTifiER_", "_QuoTed14_IdenTifiER_"),
        ("`QuoTed15 IdenTifiER`", "Snowflake", "_QUOTED15_IDENTIFIER_", "{{ adapter.quote('`QuoTed15 IdenTifiER`') }}"),
        ("`QuoTed16 IdenTifiER`", "Redshift", "_quoted16_identifier_", "{{ adapter.quote('`quoted16 identifier`') }}"),
        ("`QuoTed17 IdenTifiER`", "MySQL", "_quoted17_identifier_", "{{ adapter.quote('_QuoTed17 IdenTifiER_') }}"),
        ("`QuoTed18 IdenTifiER`", "MSSQL", "_quoted18_identifier_", "{{ adapter.quote('`QuoTed18 IdenTifiER`') }}"),
        ("`QuoTed17 IdenTifiER`", "TiDB", "_quoted17_identifier_", "{{ adapter.quote('_QuoTed17 IdenTifiER_') }}"),
    ],
)
def test_normalize_name(input_str: str, destination_type: str, expected: str, expected_column: str):
    t = DestinationType.from_string(destination_type)
    assert DestinationNameTransformer(t).normalize_schema_name(input_str) == expected
    assert DestinationNameTransformer(t).normalize_table_name(input_str) == expected
    assert DestinationNameTransformer(t).normalize_column_name(input_str) == expected_column
