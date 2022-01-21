{%- macro redshift_super_type() -%}
    {{ return(var("redshift_super_type", False) == True) }}
{%- endmacro -%}
