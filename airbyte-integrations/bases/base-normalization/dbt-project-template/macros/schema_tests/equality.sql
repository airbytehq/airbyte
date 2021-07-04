{#
-- Adapted from https://github.com/dbt-labs/dbt-utils/blob/0-19-0-updates/macros/schema_tests/equality.sql
-- dbt-utils version: 0.6.4
-- This macro needs to be updated accordingly when dbt-utils is upgraded.
-- This is needed because MySQL does not support the EXCEPT operator!
#}

{% macro mysql__test_equality(model, compare_model, compare_columns=None) %}

    {%- if not execute -%}
        {{ return('') }}
    {% endif %}

    {%- do dbt_utils._is_relation(model, 'test_equality') -%}

    {%- if not compare_columns -%}
        {%- do dbt_utils._is_ephemeral(model, 'test_equality') -%}
        {%- set compare_columns = adapter.get_columns_in_relation(model) | map(attribute='quoted') -%}
    {%- endif -%}

    {% set compare_cols_csv = compare_columns | join(', ') %}

    with a as (
        select * from {{ model }}
    ),

    b as (
        select * from {{ compare_model }}
    ),

    a_minus_b as (
        select {{ compare_cols_csv }} from a
        where ({{ compare_cols_csv }}) not in
            (select {{ compare_cols_csv }} from b)
    ),

    b_minus_a as (
        select {{ compare_cols_csv }} from b
        where ({{ compare_cols_csv }}) not in
            (select {{ compare_cols_csv }} from a)
    ),

    unioned as (
        select * from a_minus_b
        union all
        select * from b_minus_a
    ),

    final as (
        select (select count(*) from unioned) +
        (select abs(
            (select count(*) from a_minus_b) -
            (select count(*) from b_minus_a)
            ))
        as count
    )

    select count from final

{% endmacro %}
