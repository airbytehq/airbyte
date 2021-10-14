{#
    Drop schema to clean up the destination database
#}
{% macro drop_schemas(schemas) %}
  {% for schema in schemas %}
    drop schema if exists {{ schema }} cascade;
  {% endfor %}
{% endmacro %}
