
{# boolean_to_string -------------------------------------------------     #}
{% macro boolean_to_string(boolean_column) -%}
  {{ adapter.dispatch('boolean_to_string')(boolean_column) }}
{%- endmacro %}

{% macro default__boolean_to_string(boolean_column) -%}
    {{ boolean_column }}
{%- endmacro %}

{% macro redshift__boolean_to_string(boolean_column) -%}
    case when {{ boolean_column }} then 'true' else 'false' end
{%- endmacro %}

{# array_to_string -------------------------------------------------     #}
{% macro array_to_string(array_column) -%}
  {{ adapter.dispatch('array_to_string')(array_column) }}
{%- endmacro %}

{% macro default__array_to_string(array_column) -%}
    {{ array_column }}
{%- endmacro %}

{% macro bigquery__array_to_string(array_column) -%}
    array_to_string({{ array_column }}, "|", "")
{%- endmacro %}

{% macro oracle__array_to_string(array_column) -%}
    cast({{ array_column }} as varchar2(4000))
{%- endmacro %}

{% macro sqlserver__array_to_string(array_column) -%}
    cast({{ array_column }} as {{dbt_utils.type_string()}})
{%- endmacro %}

{# cast_to_boolean -------------------------------------------------     #}
{% macro cast_to_boolean(field) -%}
    {{ adapter.dispatch('cast_to_boolean')(field) }}
{%- endmacro %}

{% macro default__cast_to_boolean(field) -%}
    cast({{ field }} as boolean)
{%- endmacro %}

{# -- MySQL does not support cast function converting string directly to boolean (an alias of tinyint(1), https://dev.mysql.com/doc/refman/8.0/en/cast-functions.html#function_cast #}
{% macro mysql__cast_to_boolean(field) -%}
    IF(lower({{ field }}) = 'true', true, false)
{%- endmacro %}

{# -- Redshift does not support converting string directly to boolean, it must go through int first #}
{% macro redshift__cast_to_boolean(field) -%}
    cast(decode({{ field }}, 'true', '1', 'false', '0')::integer as boolean)
{%- endmacro %}

{# -- MS SQL Server does not support converting string directly to boolean, it must be casted as bit #}
{% macro sqlserver__cast_to_boolean(field) -%}
    cast({{ field }} as bit)
{%- endmacro %}

{# empty_string_to_null -------------------------------------------------     #}
{% macro empty_string_to_null(field) -%}
    {{ return(adapter.dispatch('empty_string_to_null')(field)) }}
{%- endmacro %}

{%- macro default__empty_string_to_null(field) -%}
    nullif({{ field }}, '')
{%- endmacro %}
