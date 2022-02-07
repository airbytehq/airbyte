{%- macro redshift_super_type() -%}
    {%- if not execute -%}
        {{ return("") }}
    {%- endif -%}

    {%- set schemaname, _, tablename = var("models_to_source")[this.identifier].partition(".") -%}

    {%- call statement("get_column_type", fetch_result=True) -%}
        set search_path to '$user', public, {{ schemaname }};
        select type from pg_table_def where tablename = '{{ tablename }}' and "column" = '{{ var("json_column") }}' and schemaname = '{{ schemaname }}';
    {%- endcall -%}

    {%- set column_type = load_result("get_column_type")["data"][0][0] -%}
    {{ return(column_type == "super") }}
{%- endmacro -%}
