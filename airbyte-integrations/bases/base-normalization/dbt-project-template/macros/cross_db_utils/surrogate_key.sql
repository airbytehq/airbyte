{# surrogate_key  ----------------------------------     #}
{% macro surrogate_key_airbyte(parent_hash_id, fields) -%}
  {{ adapter.dispatch('surrogate_key_airbyte')(fields) }}
{%- endmacro %}

{% macro default__surrogate_key_airbyte(parent_hash_id, fields) -%}

{%- endmacro %}

{% macro oracle__surrogate_key_airbyte(parent_hash_id, fields) -%}

{%- endmacro %}