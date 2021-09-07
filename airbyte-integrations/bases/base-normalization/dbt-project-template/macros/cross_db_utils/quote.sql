{# quote  ----------------------------------     #}
{% macro quote(column_name) -%}
  {{ adapter.dispatch('quote')(column_name) }}
{%- endmacro %}

{% macro default__quote(column_name) -%}
  adapter.quote(column_name)
{%- endmacro %}

{% macro oracle__quote(column_name) -%}
  {{ '\"' ~ column_name ~ '\"'}}
{%- endmacro %}
