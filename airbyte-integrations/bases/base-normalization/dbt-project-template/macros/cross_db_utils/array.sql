{#
    Adapter Macros for the following functions:
    - Bigquery: unnest() -> https://cloud.google.com/bigquery/docs/reference/standard-sql/arrays#flattening-arrays-and-repeated-fields
    - Snowflake: flatten() -> https://docs.snowflake.com/en/sql-reference/functions/flatten.html
    - Redshift: -> https://blog.getdbt.com/how-to-unnest-arrays-in-redshift/
    - postgres: unnest() -> https://www.postgresqltutorial.com/postgresql-array/
#}

{# unnest -------------------------------------------------     #}

{% macro unnest(array_col) -%}
  {{ adapter.dispatch('unnest')(array_col) }}
{%- endmacro %}

{% macro default__unnest(array_col) -%}
    unnest({{ array_col }})
{%- endmacro %}

{% macro bigquery__unnest(array_col) -%}
    unnest({{ array_col }})
{%- endmacro %}

{% macro postgres__unnest(array_col) -%}
    jsonb_array_elements(
        case jsonb_typeof({{ array_col }})
        when 'array' then {{ array_col }}
        else '[]' end
    )
{%- endmacro %}

{% macro redshift__unnest(array_col) -%}
    -- FIXME to implement as described here? https://blog.getdbt.com/how-to-unnest-arrays-in-redshift/
{%- endmacro %}

{% macro snowflake__unnest(array_col) -%}
    table(flatten({{ array_col }}))
{%- endmacro %}

{# unnested_column_value -------------------------------------------------     #}

{% macro unnested_column_value(column_col) -%}
  {{ adapter.dispatch('unnested_column_value')(column_col) }}
{%- endmacro %}

{% macro default__unnested_column_value(column_col) -%}
    {{ column_col }}
{%- endmacro %}

{% macro snowflake__unnested_column_value(column_col) -%}
    {{ column_col }}.value
{%- endmacro %}