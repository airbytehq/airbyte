{%- macro redshift_super_type() -%}
    {%- if not execute -%}
        {{ return("") }}
    {%- endif -%}

    {%- call statement("get_column_type", fetch_result=True) -%}
        select type from pg_table_def where tablename = '{{ var("models_to_source")[this.identifier] }}' and "column" = '{{ var("json_column") }}' and schemaname = '{{ target.schema }}';
    {%- endcall -%}

    {%- set column_type = load_result("get_column_type")["data"][0][0] -%}
    {{ return(column_type == "super") }}
{%- endmacro -%}
