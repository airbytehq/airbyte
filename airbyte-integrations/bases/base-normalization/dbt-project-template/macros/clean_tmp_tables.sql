-- macro to clean Redshift normalization tmp tables
{% macro redshift__clean_tmp_tables(schemas) %}
    {%- for tmp_schema in schemas -%}
        {% do log("\tDROPING SCHEMA " ~ tmp_schema, info=True) %}
        {%- set drop_query -%}
            drop schema if exists {{ tmp_schema }} cascade;
        {%- endset -%}
        {%- do run_query(drop_query) -%}
    {%- endfor -%}
{% endmacro %}