{%- macro redshift_super_type() -%}
    {%- if not execute -%}
        {{ return("") }}
    {%- endif -%}

    {%- set table_schema, _, table_name = var("models_to_source")[this.identifier].partition(".") -%}

    {%- call statement("get_column_type", fetch_result=True) -%}
        select data_type from SVV_COLUMNS where table_name = '{{ table_name }}' and column_name = '{{ var("json_column") }}' and table_schema = '{{ table_schema }}';
    {%- endcall -%}

    {%- set column_type = load_result("get_column_type")["data"][0][0] -%}
    {{ return(column_type == "super") }}
{%- endmacro -%}
