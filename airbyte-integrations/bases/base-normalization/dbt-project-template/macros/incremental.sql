{#
    These macros control how incremental models are updated in Airbyte's normalization step
    - get_max_normalized_cursor retrieve the value of the last normalized data
    - incremental_clause controls the predicate to filter on new data to process incrementally
    - alter_relation_add_remove_columns allows sync_all_columns from databricks
#}

{% macro incremental_clause(col_emitted_at, tablename)  -%}
  {{ adapter.dispatch('incremental_clause')(col_emitted_at, tablename) }}
{%- endmacro %}

{%- macro default__incremental_clause(col_emitted_at, tablename) -%}
{% if is_incremental() %}
and coalesce(
    cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }}) > (select max(cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }})) from {{ tablename }}),
    {# -- if {{ col_emitted_at }} is NULL in either table, the previous comparison would evaluate to NULL, #}
    {# -- so we coalesce and make sure the row is always returned for incremental processing instead #}
    true)
{% endif %}
{%- endmacro -%}

{# -- see https://on-systems.tech/113-beware-dbt-incremental-updates-against-snowflake-external-tables/ #}
{%- macro snowflake__incremental_clause(col_emitted_at, tablename) -%}
{% if is_incremental() %}
    {% if get_max_normalized_cursor(col_emitted_at, tablename) %}
and cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }}) >
    cast('{{ get_max_normalized_cursor(col_emitted_at, tablename) }}' as {{ type_timestamp_with_timezone() }})
    {% endif %}
{% endif %}
{%- endmacro -%}

{# -- see https://cloud.google.com/bigquery/docs/querying-partitioned-tables#best_practices_for_partition_pruning #}
{%- macro bigquery__incremental_clause(col_emitted_at, tablename) -%}
{% if is_incremental() %}
    {% if get_max_normalized_cursor(col_emitted_at, tablename) %}
and cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }}) >
    cast('{{ get_max_normalized_cursor(col_emitted_at, tablename) }}' as {{ type_timestamp_with_timezone() }})
    {% endif %}
{% endif %}
{%- endmacro -%}

{%- macro sqlserver__incremental_clause(col_emitted_at, tablename) -%}
{% if is_incremental() %}
and ((select max(cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }})) from {{ tablename }}) is null
  or cast({{ col_emitted_at }} as {{ type_timestamp_with_timezone() }}) >
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

{% macro databricks__alter_relation_add_remove_columns(relation, add_columns, remove_columns) %}
  {%- set drop_unallowed = true -%}
  {% if remove_columns %}
    {% if relation.is_delta %}
    {% set platform_name = 'Delta Lake' %}
      {%- set tblproperties = config.get('tblproperties') -%}
      {%- if not tblproperties -%}
        {%- set tblproperties = fetch_tbl_properties(relation) -%}
      {%- endif -%}
      {%- set good_predicates = 0 -%}
      {%- for prop in tblproperties -%}
        {%- if prop == 'delta.minReaderVersion' and tblproperties[prop] == 2 %-}
          {%- set good_predicates = good_predicates + 1 -%}
        {%- elif prop == 'delta.minWriterVersion' and tblproperties[prop] == 5 -%}
          {%- set good_predicates = good_predicates + 1 -%}
        {%- endif -%}
        {%- elif prop == 'delta.columnMapping.mode' and tblproperties[prop] == 'name' -%}
          {%- set good_predicates = good_predicates + 1 -%}
        {%- endif -%}
      {%- endfor -%}
      {%- if good_predicates == 3 -%}
        {%- set drop_unallowed = false -%}

      {%- endif -%}
    {%- endif -%}
    {% elif relation.is_iceberg %}
      {% set platform_name = 'Iceberg' %}
    {% else %}
      {% set platform_name = 'Apache Spark' %}
    {% endif %}
    {% if drop_unallowed %}
    {{ exceptions.raise_compiler_error(platform_name + ' does not support dropping columns from tables') }}
      {% if relation.is_delta %}
        {{ exceptions.raise_compiler_error('To allow dropping column, ensure you have tblproperties set as followed : delta.minReaderVersion: 2 / delta.minWriterVersion: 5 / delta.columnMapping.mode: name') }}
      {% endif %}
    {% endif %}
  {% endif %}

  {% if drop_columns is none %}
    {% set drop_columns = [] %}
  {% endif %}

  {% set drop_sql -%}

    alter {{ relation.type }} {{ relation }}

    {% if drop_columns %} drop columns {% endif %}
        {% for column in drop_columns %}
            {{ column.name }} {{ ',' if not loop.last }}
        {% endfor %}
  {%- endset -%}

  {% if add_columns is none %}
    {% set add_columns = [] %}
  {% endif %}

  {% set add_sql -%}

     alter {{ relation.type }} {{ relation }}

       {% if add_columns %} add columns {% endif %}
            {% for column in add_columns %}
               {{ column.name }} {{ column.data_type }}{{ ',' if not loop.last }}
            {% endfor %}

  {%- endset -%}

  {% do run_query(drop_sql) %}
  {% do run_query(add_sql) %}

{% endmacro %}