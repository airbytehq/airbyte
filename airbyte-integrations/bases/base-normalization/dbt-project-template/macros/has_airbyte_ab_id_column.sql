{% macro need_normalization_full_refresh() %}
  {%- set cols = adapter.get_columns_in_relation(this) -%}
  {%- if "airbyte_ab_id" in cols -%}
    {% do return(false) %}
  {% else %}
    {% do return(true) %}
  {% endif %}
{% endmacro %}
