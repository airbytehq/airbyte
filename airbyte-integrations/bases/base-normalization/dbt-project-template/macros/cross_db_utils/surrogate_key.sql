{#
    Overriding the following macro from dbt-utils:
        https://github.com/fishtown-analytics/dbt-utils/blob/0.6.2/macros/sql/surrogate_key.sql
    To implement our own version of concat
    Because on postgres, we cannot pass more than 100 arguments to a function
#}

{%- macro surrogate_key(field_list) -%}

{%- if varargs|length >= 1 or field_list is string %}

{%- set error_message = '
Warning: the `surrogate_key` macro now takes a single list argument instead of \
multiple string arguments. Support for multiple string arguments will be \
deprecated in a future release of dbt-utils. The {}.{} model triggered this warning. \
'.format(model.package_name, model.name) -%}

{%- do exceptions.warn(error_message) -%}

{# first argument is not included in varargs, so add first element to field_list_xf #}
{%- set field_list_xf = [field_list] -%}

{%- for field in varargs %}
{%- set _ = field_list_xf.append(field) -%}
{%- endfor -%}

{%- else -%}

{# if using list, just set field_list_xf as field_list #}
{%- set field_list_xf = field_list -%}

{%- endif -%}


{%- set fields = [] -%}

{%- for field in field_list_xf -%}

    {%- set _ = fields.append(
        "coalesce(cast(" ~ field ~ " as " ~ dbt_utils.type_string() ~ "), '')"
    ) -%}

    {%- if not loop.last %}
        {%- set _ = fields.append("'-'") -%}
    {%- endif -%}

{%- endfor -%}

{{dbt_utils.hash(concat(fields))}}

{%- endmacro -%}