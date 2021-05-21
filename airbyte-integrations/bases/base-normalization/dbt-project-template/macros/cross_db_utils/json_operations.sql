{#
    Adapter Macros for the following functions:
    - Bigquery: JSON_EXTRACT(json_string_expr, json_path_format) -> https://cloud.google.com/bigquery/docs/reference/standard-sql/json_functions
    - Snowflake: JSON_EXTRACT_PATH_TEXT( <column_identifier> , '<path_name>' ) -> https://docs.snowflake.com/en/sql-reference/functions/json_extract_path_text.html
    - Redshift: json_extract_path_text('json_string', 'path_elem' [,'path_elem'[, …] ] [, null_if_invalid ] ) -> https://docs.aws.amazon.com/redshift/latest/dg/JSON_EXTRACT_PATH_TEXT.html
    - Postgres: json_extract_path_text(<from_json>, 'path' [, 'path' [, ...}}) -> https://www.postgresql.org/docs/12/functions-json.html
#}

{# format_json_path --------------------------------------------------     #}
{% macro format_json_path(json_path_list) -%}
  {{ adapter.dispatch('format_json_path')(json_path_list) }}
{%- endmacro %}

{% macro default__format_json_path(json_path_list) -%}
  {{ '.' ~ json_path_list|join('.') }}
{%- endmacro %}

{% macro bigquery__format_json_path(json_path_list) -%}
  {{ '"$[\'' ~ json_path_list|join('\'][\'') ~ '\']"' }}
{%- endmacro %}

{% macro postgres__format_json_path(json_path_list) -%}
 {{ "'" ~ json_path_list|join("','") ~ "'" }}
{%- endmacro %}

{% macro redshift__format_json_path(json_path_list) -%}
 {{ "'" ~ json_path_list|join("','") ~ "'" }}
{%- endmacro %}

{% macro snowflake__format_json_path(json_path_list) -%}
  {{ "'\"" ~ json_path_list|join('"."') ~ "\"'" }}
{%- endmacro %}

{# json_extract -------------------------------------------------     #}

{% macro json_extract(json_column, json_path_list) -%}
  {{ adapter.dispatch('json_extract')(json_column, json_path_list) }}
{%- endmacro %}

{% macro default__json_extract(json_column, json_path_list) -%}
    json_extract({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro bigquery__json_extract(json_column, json_path_list) -%}
    json_extract({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro postgres__json_extract(json_column, json_path_list) -%}
    jsonb_extract_path({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro redshift__json_extract(json_column, json_path_list) -%}
    case when json_extract_path_text({{ json_column }}, {{ format_json_path(json_path_list) }}, true) != '' then json_extract_path_text({{ json_column }}, {{ format_json_path(json_path_list) }}, true) end
{%- endmacro %}

{% macro snowflake__json_extract(json_column, json_path_list) -%}
    get_path(parse_json({{ json_column }}), {{ format_json_path(json_path_list) }})
{%- endmacro %}

{# json_extract_scalar -------------------------------------------------     #}

{% macro json_extract_scalar(json_column, json_path_list) -%}
  {{ adapter.dispatch('json_extract_scalar')(json_column, json_path_list) }}
{%- endmacro %}

{% macro default__json_extract_scalar(json_column, json_path_list) -%}
    json_extract_scalar({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro bigquery__json_extract_scalar(json_column, json_path_list) -%}
    json_extract_scalar({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro postgres__json_extract_scalar(json_column, json_path_list) -%}
    jsonb_extract_path_text({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro redshift__json_extract_scalar(json_column, json_path_list) -%}
    case when json_extract_path_text({{ json_column }}, {{ format_json_path(json_path_list) }}, true) != '' then json_extract_path_text({{ json_column }}, {{ format_json_path(json_path_list) }}, true) end
{%- endmacro %}

{% macro snowflake__json_extract_scalar(json_column, json_path_list) -%}
    to_varchar(get_path(parse_json({{ json_column }}), {{ format_json_path(json_path_list) }}))
{%- endmacro %}

{# json_extract_array -------------------------------------------------     #}

{% macro json_extract_array(json_column, json_path_list) -%}
  {{ adapter.dispatch('json_extract_array')(json_column, json_path_list) }}
{%- endmacro %}

{% macro default__json_extract_array(json_column, json_path_list) -%}
    json_extract_array({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro bigquery__json_extract_array(json_column, json_path_list) -%}
    json_extract_array({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro postgres__json_extract_array(json_column, json_path_list) -%}
    jsonb_extract_path({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro redshift__json_extract_array(json_column, json_path_list) -%}
    json_extract_path_text({{ json_column }}, {{ format_json_path(json_path_list) }}, true)
{%- endmacro %}

{% macro snowflake__json_extract_array(json_column, json_path_list) -%}
    get_path(parse_json({{ json_column }}), {{ format_json_path(json_path_list) }})
{%- endmacro %}
