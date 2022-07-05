{#
    Adapter Macros for the following functions:
    - Bigquery: unnest() -> https://cloud.google.com/bigquery/docs/reference/standard-sql/arrays#flattening-arrays-and-repeated-fields
    - Snowflake: flatten() -> https://docs.snowflake.com/en/sql-reference/functions/flatten.html
    - Redshift: -> https://blog.getdbt.com/how-to-unnest-arrays-in-redshift/
    - postgres: unnest() -> https://www.postgresqltutorial.com/postgresql-array/
    - MSSQL: openjson() –> https://docs.microsoft.com/en-us/sql/relational-databases/json/validate-query-and-change-json-data-with-built-in-functions-sql-server?view=sql-server-ver15
    - ClickHouse: ARRAY JOIN –> https://clickhouse.com/docs/zh/sql-reference/statements/select/array-join/
#}

{# cross_join_unnest -------------------------------------------------     #}

{% macro cross_join_unnest(stream_name, array_col) -%}
  {{ adapter.dispatch('cross_join_unnest')(stream_name, array_col) }}
{%- endmacro %}

{% macro default__cross_join_unnest(stream_name, array_col) -%}
    {% do exceptions.warn("Undefined macro cross_join_unnest for this destination engine") %}
{%- endmacro %}

{% macro bigquery__cross_join_unnest(stream_name, array_col) -%}
    cross join unnest({{ array_col }}) as {{ array_col }}
{%- endmacro %}

{% macro clickhouse__cross_join_unnest(stream_name, array_col) -%}
    ARRAY JOIN {{ array_col }}
{%- endmacro %}

{% macro oracle__cross_join_unnest(stream_name, array_col) -%}
    {% do exceptions.warn("Normalization does not support unnesting for Oracle yet.") %}
{%- endmacro %}

{% macro postgres__cross_join_unnest(stream_name, array_col) -%}
    cross join jsonb_array_elements(
        case jsonb_typeof({{ array_col }})
        when 'array' then {{ array_col }}
        else '[]' end
    ) as _airbyte_nested_data
{%- endmacro %}

{% macro mysql__cross_join_unnest(stream_name, array_col) -%}
    left join joined on _airbyte_{{ stream_name }}_hashid = joined._airbyte_hashid
{%- endmacro %}

{% macro redshift__cross_join_unnest(stream_name, array_col) -%}
    left join joined on _airbyte_{{ stream_name }}_hashid = joined._airbyte_hashid
{%- endmacro %}

{% macro snowflake__cross_join_unnest(stream_name, array_col) -%}
    cross join table(flatten({{ array_col }})) as {{ array_col }}
{%- endmacro %}

{% macro sqlserver__cross_join_unnest(stream_name, array_col) -%}
{# https://docs.microsoft.com/en-us/sql/relational-databases/json/convert-json-data-to-rows-and-columns-with-openjson-sql-server?view=sql-server-ver15#option-1---openjson-with-the-default-output #}
    CROSS APPLY (
	    SELECT [value] = CASE
			WHEN [type] = 4 THEN (SELECT [value] FROM OPENJSON([value]))
			WHEN [type] = 5 THEN [value]
			END
	    FROM OPENJSON({{ array_col }})
    ) AS {{ array_col }}
{%- endmacro %}

{# unnested_column_value -- this macro is related to unnest_cte #}

{% macro unnested_column_value(column_col) -%}
  {{ adapter.dispatch('unnested_column_value')(column_col) }}
{%- endmacro %}

{% macro default__unnested_column_value(column_col) -%}
    {{ column_col }}
{%- endmacro %}

{% macro postgres__unnested_column_value(column_col) -%}
    _airbyte_nested_data
{%- endmacro %}

{% macro snowflake__unnested_column_value(column_col) -%}
    {{ column_col }}.value
{%- endmacro %}

{% macro redshift__unnested_column_value(column_col) -%}
    _airbyte_nested_data
{%- endmacro %}

{% macro mysql__unnested_column_value(column_col) -%}
    _airbyte_nested_data
{%- endmacro %}

{% macro oracle__unnested_column_value(column_col) -%}
    {{ column_col }}
{%- endmacro %}

{% macro sqlserver__unnested_column_value(column_col) -%}
    {# unnested array/sub_array will be located in `value` column afterwards, we need to address to it #}
    {{ column_col }}.value
{%- endmacro %}

{# unnest_cte -------------------------------------------------     #}

{% macro unnest_cte(from_table, stream_name, column_col) -%}
  {{ adapter.dispatch('unnest_cte')(from_table, stream_name, column_col) }}
{%- endmacro %}

{% macro default__unnest_cte(from_table, stream_name, column_col) -%}{%- endmacro %}

{% macro redshift__unnest_cte(from_table, stream_name, column_col) -%}

    {# -- based on https://docs.aws.amazon.com/redshift/latest/dg/query-super.html #}
    {% if redshift_super_type() -%}
        with joined as (
            select
                table_alias._airbyte_{{ stream_name }}_hashid as _airbyte_hashid,
                _airbyte_nested_data
            from {{ from_table }} as table_alias, table_alias.{{ column_col }} as _airbyte_nested_data
        )
    {%- else -%}

    {# -- based on https://blog.getdbt.com/how-to-unnest-arrays-in-redshift/ #}
    {%- if not execute -%}
        {{ return('') }}
    {% endif %}
    {%- call statement('max_json_array_length', fetch_result=True) -%}
        with max_value as (
            select max(json_array_length({{ column_col }}, true)) as max_number_of_items
            from {{ from_table }}
        )
        select
            case when max_number_of_items is not null and max_number_of_items > 1
            then max_number_of_items
            else 1 end as max_number_of_items
        from max_value
    {%- endcall -%}
    {%- set max_length = load_result('max_json_array_length') -%}
with numbers as (
    {{dbt_utils.generate_series(max_length["data"][0][0])}}
),
joined as (
    select
        _airbyte_{{ stream_name }}_hashid as _airbyte_hashid,
        json_extract_array_element_text({{ column_col }}, numbers.generated_number::int - 1, true) as _airbyte_nested_data
    from {{ from_table }}
    cross join numbers
    -- only generate the number of records in the cross join that corresponds
    -- to the number of items in {{ from_table }}.{{ column_col }}
    where numbers.generated_number <= json_array_length({{ column_col }}, true)
)
    {%- endif %}
{%- endmacro %}

{% macro mysql__unnest_cte(from_table, stream_name, column_col) -%}
    {%- if not execute -%}
        {{ return('') }}
    {% endif %}

    {%- call statement('max_json_array_length', fetch_result=True) -%}
        with max_value as (
            select max(json_length({{ column_col }})) as max_number_of_items
            from {{ from_table }}
        )
        select
            case when max_number_of_items is not null and max_number_of_items > 1
            then max_number_of_items
            else 1 end as max_number_of_items
        from max_value
    {%- endcall -%}

    {%- set max_length = load_result('max_json_array_length') -%}
    with numbers as (
        {{ dbt_utils.generate_series(max_length["data"][0][0]) }}
    ),
    joined as (
        select
            _airbyte_{{ stream_name }}_hashid as _airbyte_hashid,
            {# -- json_extract(column_col, '$[i][0]') as _airbyte_nested_data #}
            json_extract({{ column_col }}, concat("$[", numbers.generated_number - 1, "][0]")) as _airbyte_nested_data
        from {{ from_table }}
        cross join numbers
        -- only generate the number of records in the cross join that corresponds
        -- to the number of items in {{ from_table }}.{{ column_col }}
        where numbers.generated_number <= json_length({{ column_col }})
    )
{%- endmacro %}
