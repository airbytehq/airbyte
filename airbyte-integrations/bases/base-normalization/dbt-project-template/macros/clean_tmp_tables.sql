{% macro clean_tmp_tables(schemas) -%}
  {{ adapter.dispatch('clean_tmp_tables')(schemas) }}
{%- endmacro %}

-- default
{% macro default__clean_tmp_tables(schemas) -%}
    {% do exceptions.warn("\tINFO: CLEANING TEST LEFTOVERS IS NOT IMPLEMENTED FOR THIS DESTINATION. CONSIDER TO REMOVE TEST TABLES MANUALY.\n") %}
{%- endmacro %}

-- for redshift
{% macro redshift__clean_tmp_tables(schemas) %}
    {%- for tmp_schema in schemas -%}
        {% do log("\tDROP SCHEMA IF EXISTS " ~ tmp_schema, info=True) %}
        {%- set drop_query -%}
            drop schema if exists {{ tmp_schema }} cascade;
        {%- endset -%}
        {%- do run_query(drop_query) -%}
    {%- endfor -%}
{% endmacro %}