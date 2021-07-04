{# json  -------------------------------------------------     #}

{%- macro type_json() -%}
  {{ adapter.dispatch('type_json')() }}
{%- endmacro -%}

{% macro default__type_json() %}
    string
{% endmacro %}

{%- macro redshift__type_json() -%}
    varchar
{%- endmacro -%}

{% macro postgres__type_json() %}
    jsonb
{% endmacro %}

{% macro snowflake__type_json() %}
    variant
{% endmacro %}

{%- macro mysql__type_json() -%}
    json
{%- endmacro -%}


{# string ------------------------------------------------- #}

{%- macro mysql__type_string() -%}
    char
{%- endmacro -%}


{# float ------------------------------------------------- #}
{% macro mysql__type_float() %}
    float
{% endmacro %}


{# int  ------------------------------------------------- #}
{% macro default__type_int() %}
    signed
{% endmacro %}


{# bigint ------------------------------------------------- #}
{% macro mysql__type_bigint() %}
    signed
{% endmacro %}


{# numeric ------------------------------------------------- #}
{% macro mysql__type_numeric() %}
    float
{% endmacro %}


{# timestamp ------------------------------------------------- #}
{% macro mysql__type_timestamp() %}
    time
{% endmacro %}
