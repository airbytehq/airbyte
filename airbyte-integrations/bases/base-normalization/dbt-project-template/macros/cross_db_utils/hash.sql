{# converting hash in varchar _macro #}

{% macro sqlserver__hash(field) -%}
    convert(varchar(32), HashBytes('md5',  coalesce(cast({{field}} as {{dbt_utils.type_string()}}), '')), 2)
{%- endmacro %}