{#
    Adapter Macros for the following functions:
    - Bigquery: JSON_EXTRACT(json_string_expr, json_path_format) -> https://cloud.google.com/bigquery/docs/reference/standard-sql/json_functions
    - Snowflake: JSON_EXTRACT_PATH_TEXT( <column_identifier> , '<path_name>' ) -> https://docs.snowflake.com/en/sql-reference/functions/json_extract_path_text.html
    - Redshift: json_extract_path_text('json_string', 'path_elem' [,'path_elem'[, ...] ] [, null_if_invalid ] ) -> https://docs.aws.amazon.com/redshift/latest/dg/JSON_EXTRACT_PATH_TEXT.html
    - Postgres: json_extract_path_text(<from_json>, 'path' [, 'path' [, ...}}) -> https://www.postgresql.org/docs/12/functions-json.html
    - MySQL: JSON_EXTRACT(json_doc, 'path' [, 'path'] ...) -> https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html
#}

{# format_json_path --------------------------------------------------     #}
{% macro format_json_path(json_path_list) -%}
    {{ adapter.dispatch('format_json_path')(json_path_list) }}
{%- endmacro %}

{% macro default__format_json_path(json_path_list) -%}
    {{ '.' ~ json_path_list|join('.') }}
{%- endmacro %}

{% macro oracle__format_json_path(json_path_list) -%}
  {{ '\'$."' ~ json_path_list|join('."') ~ '"\'' }}
{%- endmacro %}

{% macro bigquery__format_json_path(json_path_list) -%}
    {%- set str_list = [] -%}
    {%- for json_path in json_path_list -%}
        {%- if str_list.append(json_path.replace('"', '\\"')) -%} {%- endif -%}
    {%- endfor -%}
    {{ '"$[\'' ~ str_list|join('\'][\'') ~ '\']"' }}
{%- endmacro %}

{% macro postgres__format_json_path(json_path_list) -%}
    {%- set str_list = [] -%}
    {%- for json_path in json_path_list -%}
        {%- if str_list.append(json_path.replace("'", "''")) -%} {%- endif -%}
    {%- endfor -%}
    {{ "'" ~ str_list|join("','") ~ "'" }}
{%- endmacro %}

{% macro mysql__format_json_path(json_path_list) -%}
    {# -- '$."x"."y"."z"' #}
    {{ "'$.\"" ~ json_path_list|join(".") ~ "\"'" }}
{%- endmacro %}

{% macro redshift__format_json_path(json_path_list) -%}
    {%- set str_list = [] -%}
    {%- for json_path in json_path_list -%}
        {%- if str_list.append(json_path.replace("'", "''")) -%} {%- endif -%}
    {%- endfor -%}
    {{ "'" ~ str_list|join("','") ~ "'" }}
{%- endmacro %}

{% macro snowflake__format_json_path(json_path_list) -%}
    {%- set str_list = [] -%}
    {%- for json_path in json_path_list -%}
        {%- if str_list.append(json_path.replace("'", "''").replace('"', '""')) -%} {%- endif -%}
    {%- endfor -%}
    {{ "'\"" ~ str_list|join('"."') ~ "\"'" }}
{%- endmacro %}

{% macro sqlserver__format_json_path(json_path_list) -%}
    {# -- '$."x"."y"."z"' #}
    {%- set str_list = [] -%}
    {%- for json_path in json_path_list -%}
        {%- if str_list.append(json_path.replace("'", "''").replace('"', '\\"')) -%} {%- endif -%}
    {%- endfor -%}
    {{ "'$.\"" ~ str_list|join(".") ~ "\"'" }}
{%- endmacro %}

{# json_extract -------------------------------------------------     #}

{% macro json_extract(from_table, json_column, json_path_list, normalized_json_path) -%}
    {{ adapter.dispatch('json_extract')(from_table, json_column, json_path_list, normalized_json_path) }}
{%- endmacro %}

{% macro default__json_extract(from_table, json_column, json_path_list, normalized_json_path) -%}
    json_extract({{ from_table}}.{{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro oracle__json_extract(from_table, json_column, json_path_list, normalized_json_path) -%}
    json_value({{ json_column }}, {{ format_json_path(normalized_json_path) }})
{%- endmacro %}

{% macro bigquery__json_extract(from_table, json_column, json_path_list, normalized_json_path) -%}
    {%- if from_table|string() == '' %}
        json_extract({{ json_column }}, {{ format_json_path(normalized_json_path) }})
    {% else %}
        json_extract({{ from_table}}.{{ json_column }}, {{ format_json_path(normalized_json_path) }})
    {% endif -%}
{%- endmacro %}

{% macro postgres__json_extract(from_table, json_column, json_path_list, normalized_json_path) -%}
    {%- if from_table|string() == '' %}
        jsonb_extract_path({{ json_column }}, {{ format_json_path(json_path_list) }})
    {% else %}
        jsonb_extract_path({{ from_table }}.{{ json_column }}, {{ format_json_path(json_path_list) }})
    {% endif -%}
{%- endmacro %}

{% macro mysql__json_extract(from_table, json_column, json_path_list, normalized_json_path) -%}
    {%- if from_table|string() == '' %}
        json_extract({{ json_column }}, {{ format_json_path(normalized_json_path) }})
    {% else %}
        json_extract({{ from_table }}.{{ json_column }}, {{ format_json_path(normalized_json_path) }})
    {% endif -%}
{%- endmacro %}

{% macro redshift__json_extract(from_table, json_column, json_path_list, normalized_json_path) -%}
    {%- if from_table|string() == '' %}
        case when json_extract_path_text({{ json_column }}, {{ format_json_path(json_path_list) }}, true) != '' then json_extract_path_text({{ json_column }}, {{ format_json_path(json_path_list) }}, true) end
    {% else %}
        case when json_extract_path_text({{ from_table }}.{{ json_column }}, {{ format_json_path(json_path_list) }}, true) != '' then json_extract_path_text({{ from_table }}.{{ json_column }}, {{ format_json_path(json_path_list) }}, true) end
    {% endif -%}
{%- endmacro %}

{% macro snowflake__json_extract(from_table, json_column, json_path_list, normalized_json_path) -%}
    {%- if from_table|string() == '' %}
        get_path(parse_json({{ json_column }}), {{ format_json_path(json_path_list) }})
    {% else %}
        get_path(parse_json({{ from_table }}.{{ json_column }}), {{ format_json_path(json_path_list) }})
    {% endif -%}
{%- endmacro %}

{% macro sqlserver__json_extract(from_table, json_column, json_path_list, normalized_json_path) -%}
    json_query({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{# json_extract_scalar -------------------------------------------------     #}

{% macro json_extract_scalar(json_column, json_path_list, normalized_json_path) -%}
    {{ adapter.dispatch('json_extract_scalar')(json_column, json_path_list, normalized_json_path) }}
{%- endmacro %}

{% macro default__json_extract_scalar(json_column, json_path_list, normalized_json_path) -%}
    json_extract_scalar({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro oracle__json_extract_scalar(json_column, json_path_list, normalized_json_path) -%}
    json_value({{ json_column }}, {{ format_json_path(normalized_json_path) }})
{%- endmacro %}

{% macro bigquery__json_extract_scalar(json_column, json_path_list, normalized_json_path) -%}
    json_extract_scalar({{ json_column }}, {{ format_json_path(normalized_json_path) }})
{%- endmacro %}

{% macro postgres__json_extract_scalar(json_column, json_path_list, normalized_json_path) -%}
    jsonb_extract_path_text({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro mysql__json_extract_scalar(json_column, json_path_list, normalized_json_path) -%}
    json_value({{ json_column }}, {{ format_json_path(normalized_json_path) }})
{%- endmacro %}

{% macro redshift__json_extract_scalar(json_column, json_path_list, normalized_json_path) -%}
    case when json_extract_path_text({{ json_column }}, {{ format_json_path(json_path_list) }}, true) != '' then json_extract_path_text({{ json_column }}, {{ format_json_path(json_path_list) }}, true) end
{%- endmacro %}

{% macro snowflake__json_extract_scalar(json_column, json_path_list, normalized_json_path) -%}
    to_varchar(get_path(parse_json({{ json_column }}), {{ format_json_path(json_path_list) }}))
{%- endmacro %}

{% macro sqlserver__json_extract_scalar(json_column, json_path_list, normalized_json_path) -%}
    json_value({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{# json_extract_array -------------------------------------------------     #}

{% macro json_extract_array(json_column, json_path_list, normalized_json_path) -%}
    {{ adapter.dispatch('json_extract_array')(json_column, json_path_list, normalized_json_path) }}
{%- endmacro %}

{% macro default__json_extract_array(json_column, json_path_list, normalized_json_path) -%}
    json_extract_array({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro oracle__json_extract_array(json_column, json_path_list, normalized_json_path) -%}
    json_value({{ json_column }}, {{ format_json_path(normalized_json_path) }})
{%- endmacro %}

{% macro bigquery__json_extract_array(json_column, json_path_list, normalized_json_path) -%}
    json_extract_array({{ json_column }}, {{ format_json_path(normalized_json_path) }})
{%- endmacro %}

{% macro postgres__json_extract_array(json_column, json_path_list, normalized_json_path) -%}
    jsonb_extract_path({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro mysql__json_extract_array(json_column, json_path_list, normalized_json_path) -%}
    json_extract({{ json_column }}, {{ format_json_path(normalized_json_path) }})
{%- endmacro %}

{% macro redshift__json_extract_array(json_column, json_path_list, normalized_json_path) -%}
    json_extract_path_text({{ json_column }}, {{ format_json_path(json_path_list) }}, true)
{%- endmacro %}

{% macro snowflake__json_extract_array(json_column, json_path_list, normalized_json_path) -%}
    get_path(parse_json({{ json_column }}), {{ format_json_path(json_path_list) }})
{%- endmacro %}

{% macro sqlserver__json_extract_array(json_column, json_path_list, normalized_json_path) -%}
    json_query({{ json_column }}, {{ format_json_path(json_path_list) }})
{%- endmacro %}
