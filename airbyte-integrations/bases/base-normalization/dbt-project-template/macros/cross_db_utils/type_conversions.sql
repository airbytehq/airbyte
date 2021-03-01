
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

{# cast_to_boolean -------------------------------------------------     #}
{% macro cast_to_boolean(field) -%}
    {{ adapter.dispatch('cast_to_boolean')(field) }}
{%- endmacro %}

{% macro default__cast_to_boolean(field) -%}
    cast({{ field }} as boolean)
{%- endmacro %}

{# -- Redshift does not support converting string directly to boolean, it must go through int first #}
{% macro redshift__cast_to_boolean(field) -%}
    cast(decode({{ field }}, 'true', '1', 'false', '0')::integer as boolean)
{%- endmacro %}
