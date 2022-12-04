{#
    These macros control how incremental models are updated in Airbyte's normalization step
    - get_max_normalized_cursor retrieve the value of the last normalized data
    - incremental_clause controls the predicate to filter on new data to process incrementally
#}

{% macro incremental_clause(col_emitted_at, tablename)  -%}
  {{ adapter.dispatch('incremental_clause')(col_emitted_at, tablename) }}
{%- endmacro %}

{%- macro default__incremental_clause(col_emitted_at, tablename) -%}
{% if is_incremental() %}
and coalesce(
    cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }}) >= (select max(cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }})) from {{ tablename }}),
    {# -- if {{ col_emitted_at }} is NULL in either table, the previous comparison would evaluate to NULL, #}
    {# -- so we coalesce and make sure the row is always returned for incremental processing instead #}
    true)
{% endif %}
{%- endmacro -%}

{# -- see https://on-systems.tech/113-beware-dbt-incremental-updates-against-snowflake-external-tables/ #}
{%- macro snowflake__incremental_clause(col_emitted_at, tablename) -%}
{% if is_incremental() %}
    {% if get_max_normalized_cursor(col_emitted_at, tablename) %}
and cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }}) >=
    cast('{{ get_max_normalized_cursor(col_emitted_at, tablename) }}' as {{ type_timestamp_with_timezone() }})
    {% endif %}
{% endif %}
{%- endmacro -%}

{# -- see https://cloud.google.com/bigquery/docs/querying-partitioned-tables#best_practices_for_partition_pruning #}
{%- macro bigquery__incremental_clause(col_emitted_at, tablename) -%}
{% if is_incremental() %}
    {% if get_max_normalized_cursor(col_emitted_at, tablename) %}
and cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }}) >=
    cast('{{ get_max_normalized_cursor(col_emitted_at, tablename) }}' as {{ type_timestamp_with_timezone() }})
    {% endif %}
{% endif %}
{%- endmacro -%}

{%- macro sqlserver__incremental_clause(col_emitted_at, tablename) -%}
{% if is_incremental() %}
and ((select max(cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }})) from {{ tablename }}) is null
  or cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }}) >=
     (select max(cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }})) from {{ tablename }}))
{% endif %}
{%- endmacro -%}

{% macro get_max_normalized_cursor(col_emitted_at, tablename) %}
{% if execute and is_incremental() %}
 {% if env_var('INCREMENTAL_CURSOR', 'UNSET') == 'UNSET' %}
     {% set query %}
        select max(cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }})) from {{ tablename }}
     {% endset %}
     {% set max_cursor = run_query(query).columns[0][0] %}
     {% do return(max_cursor) %}
 {% else %}
    {% do return(env_var('INCREMENTAL_CURSOR')) %}
 {% endif %}
{% endif %}
{% endmacro %}
