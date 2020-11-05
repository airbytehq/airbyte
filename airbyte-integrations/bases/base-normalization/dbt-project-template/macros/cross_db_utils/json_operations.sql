{#
    Adapter Macros for the following functions:
    - Bigquery: JSON_EXTRACT(json_string_expr, json_path_format) -> https://cloud.google.com/bigquery/docs/reference/standard-sql/json_functions
    - Snowflake: JSON_EXTRACT_PATH_TEXT( <column_identifier> , '<path_name>' ) -> https://docs.snowflake.com/en/sql-reference/functions/json_extract_path_text.html
    - Redshift: json_extract_path_text('json_string', 'path_elem' [,'path_elem'[, …] ] [, null_if_invalid ] ) -> https://docs.aws.amazon.com/redshift/latest/dg/JSON_EXTRACT_PATH_TEXT.html
#}

{# json_extract -------------------------------------------------     #}

{% macro json_extract(json_column, json_path) -%}
  {{ adapter.dispatch('json_extract')(json_column, json_path) }}
{%- endmacro %}

{% macro default__json_extract(json_column, json_path) -%}
    json_extract({{json_column}}, {{json_path}})
{%- endmacro %}

{% macro bigquery__json_extract(json_column, json_path) -%}
    json_extract({{json_column}}, {{json_path}})
{%- endmacro %}

{% macro redshift__json_extract(json_column, json_path) -%}
    json_extract_path_text({{json_column}}, {{json_path}})
{%- endmacro %}

{% macro snowflake__json_extract(json_column, json_path) -%}
    json_extract_path_text({{json_column}}, {{json_path}})
{%- endmacro %}

{# json_extract_scalar -------------------------------------------------     #}

{% macro json_extract_scalar(json_column, json_path) -%}
  {{ adapter.dispatch('json_extract_scalar')(json_column, json_path) }}
{%- endmacro %}

{% macro default__json_extract_scalar(json_column, json_path) -%}
    json_extract_scalar({{json_column}}, {{json_path}})
{%- endmacro %}

{% macro bigquery__json_extract_scalar(json_column, json_path) -%}
    json_extract_scalar({{json_column}}, {{json_path}})
{%- endmacro %}

{% macro redshift__json_extract_scalar(json_column, json_path) -%}
    json_extract_path_text({{json_column}}, {{json_path}})
{%- endmacro %}

{% macro snowflake__json_extract_scalar(json_column, json_path) -%}
    json_extract_path_text({{json_column}}, {{json_path}})
{%- endmacro %}

{# json_extract_array -------------------------------------------------     #}

{% macro json_extract_array(json_column, json_path) -%}
  {{ adapter.dispatch('json_extract_array')(json_column, json_path) }}
{%- endmacro %}

{% macro default__json_extract_array(json_column, json_path) -%}
    json_extract_array({{json_column}}, {{json_path}})
{%- endmacro %}

{% macro bigquery__json_extract_array(json_column, json_path) -%}
    json_extract_array({{json_column}}, {{json_path}})
{%- endmacro %}

{% macro redshift__json_extract_array(json_column, json_path) -%}
    json_extract_path_text({{json_column}}, {{json_path}})
{%- endmacro %}

{% macro snowflake__json_extract_array(json_column, json_path) -%}
    json_extract_path_text({{json_column}}, {{json_path}})
{%- endmacro %}
