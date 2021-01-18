
{# boolean_to_varchar -------------------------------------------------     #}
{% macro boolean_to_varchar(boolean_column) -%}
  {{ adapter.dispatch('boolean_to_varchar')(boolean_column) }}
{%- endmacro %}

{% macro default__boolean_to_varchar(boolean_column) -%}
    {{ boolean_column }}
{%- endmacro %}

{% macro redshift__boolean_to_varchar(boolean_column) -%}
    case when {{ boolean_column }} then 'true' else 'false' end
{%- endmacro %}

{# cast_to_boolean -------------------------------------------------     #}
{% macro cast_to_boolean(field) -%}
    {{ adapter.dispatch('cast_to_boolean')(field) }}
{%- endmacro %}

{% macro default__cast_to_boolean(field) -%}
    cast({{ field }} as boolean)
{%- endmacro %}

{# -- Redshift does not support converting varchar directly to boolean, it must go through int first #}
{% macro redshift__cast_to_boolean(field) -%}
    cast(decode({{ field }}, 'true', '1', 'false', '0')::integer as boolean)
{%- endmacro %}
