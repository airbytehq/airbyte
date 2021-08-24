{# surrogate_key  ----------------------------------     #}
{% macro QUOTE(column_name) -%}
  {{ adapter.dispatch('QUOTE')(column_name) }}
{%- endmacro %}

{% macro default__QUOTE(column_name) -%}
  adapter.quote(column_name)
{%- endmacro %}

{% macro oracle__QUOTE(column_name) -%}
  {{ '\"' ~ column_name ~ '\"'}}
{%- endmacro %}
