{#
    These macros control how incremental models are updated in Airbyte's normalization step
    - get_max_normalized_cursor retrieve the value of the last normalized data
    - incremental_clause controls the predicate to filter on new data to process incrementally
#}

{#
    columnname - the column to use as the cursor
    tablename - the table we want to extract data from
    comparisonOperator - Controls cursor values to extract. Typically either ">" or ">=", depending on how strong the cursor guarantees are.
#}
{% macro incremental_clause(columnname, tablename, comparisonOperator)  -%}
  {{ adapter.dispatch('incremental_clause')(columnname, tablename, comparisonOperator) }}
{%- endmacro %}

{%- macro default__incremental_clause(columnname, tablename, comparisonOperator) -%}
{% if is_incremental() %}
and coalesce(
    cast({{ columnname }} as {{ type_timestamp_with_timezone() }}) {{ comparisonOperator }} (select max(cast({{ columnname }} as {{ type_timestamp_with_timezone() }})) from {{ tablename }}),
    {# -- if {{ columnname }} is NULL in either table, the previous comparison would evaluate to NULL, #}
    {# -- so we coalesce and make sure the row is always returned for incremental processing instead #}
    true)
{% endif %}
{%- endmacro -%}

{# -- see https://on-systems.tech/113-beware-dbt-incremental-updates-against-snowflake-external-tables/ #}
{%- macro snowflake__incremental_clause(columnname, tablename, comparisonOperator) -%}
{% if is_incremental() %}
    {% if get_max_normalized_cursor(columnname, tablename) %}
and cast({{ columnname }} as {{ type_timestamp_with_timezone() }}) {{ comparisonOperator }}
    cast('{{ get_max_normalized_cursor(columnname, tablename) }}' as {{ type_timestamp_with_timezone() }})
    {% endif %}
{% endif %}
{%- endmacro -%}

{# -- see https://cloud.google.com/bigquery/docs/querying-partitioned-tables#best_practices_for_partition_pruning #}
{%- macro bigquery__incremental_clause(columnname, tablename, comparisonOperator) -%}
{% if is_incremental() %}
    {% if get_max_normalized_cursor(columnname, tablename) %}
and cast({{ columnname }} as {{ type_timestamp_with_timezone() }}) {{ comparisonOperator }}
    cast('{{ get_max_normalized_cursor(columnname, tablename) }}' as {{ type_timestamp_with_timezone() }})
    {% endif %}
{% endif %}
{%- endmacro -%}

{%- macro sqlserver__incremental_clause(columnname, tablename, comparisonOperator) -%}
{% if is_incremental() %}
and ((select max(cast({{ columnname }} as {{ type_timestamp_with_timezone() }})) from {{ tablename }}) is null
  or cast({{ columnname }} as {{ type_timestamp_with_timezone() }}) {{ comparisonOperator }}
     (select max(cast({{ columnname }} as {{ type_timestamp_with_timezone() }})) from {{ tablename }}))
{% endif %}
{%- endmacro -%}

{% macro get_max_normalized_cursor(columnname, tablename) %}
{% if execute and is_incremental() %}
 {% if env_var('INCREMENTAL_CURSOR', 'UNSET') == 'UNSET' %}
     {% set query %}
        select max(cast({{ columnname }} as {{ type_timestamp_with_timezone() }})) from {{ tablename }}
     {% endset %}
     {% set max_cursor = run_query(query).columns[0][0] %}
     {% do return(max_cursor) %}
 {% else %}
    {% do return(env_var('INCREMENTAL_CURSOR')) %}
 {% endif %}
{% endif %}
{% endmacro %}
