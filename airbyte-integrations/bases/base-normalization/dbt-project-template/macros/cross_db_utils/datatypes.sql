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

{%- macro oracle__type_json() -%}
    varchar2(4000)
{%- endmacro -%}

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

{%- macro oracle__type_string() -%}
    varchar2(4000)
{%- endmacro -%}


{# float ------------------------------------------------- #}
{% macro mysql__type_float() %}
    float
{% endmacro %}

{% macro oracle__type_float() %}
    float
{% endmacro %}


{# int  ------------------------------------------------- #}
{% macro default__type_int() %}
    signed
{% endmacro %}

{% macro oracle__type_int() %}
    int
{% endmacro %}

{# bigint ------------------------------------------------- #}
{% macro mysql__type_bigint() %}
    signed
{% endmacro %}

{% macro oracle__type_bigint() %}
    numeric
{% endmacro %}


{# numeric ------------------------------------------------- #}
{% macro mysql__type_numeric() %}
    float
{% endmacro %}


{# timestamp ------------------------------------------------- #}
{% macro mysql__type_timestamp() %}
    time
{% endmacro %}


{# timestamp with time zone  -------------------------------------------------     #}

{%- macro type_timestamp_with_timezone(timestamp_column) -%}
  {{ adapter.dispatch('type_timestamp_with_timezone')(timestamp_column) }}
{%- endmacro -%}

{% macro default__type_timestamp_with_timezone(timestamp_column) %}
    timestamp with time zone
{% endmacro %}

{% macro bigquery__type_timestamp_with_timezone(timestamp_column) %}
    timestamp
{% endmacro %}

{# MySQL doesnt allow cast operation to work with TIMESTAMP so we have to use char #}
{%- macro mysql__type_timestamp_with_timezone(timestamp_column) -%}
    char
{%- endmacro -%}

{% macro oracle__type_timestamp_with_timezone(timestamp_column) %}
    varchar2(4000)
{% endmacro %}

{% macro snowflake__type_timestamp_with_timezone(timestamp_column) %}
    case
        when {{timestamp_column}} regexp '[0-9]{4}-[0-9]{2}-[0-9]{2} ([0-9]{2}:){2}[0-9]{2} UTC' then to_timestamp_tz({{timestamp_column}} || '+0', 'YYYY-MM-DD HH24:MI:SS UTC TZH')

        when {{timestamp_column}} regexp '[0-9]{4}-[0-9]{2}-[0-9]{2}T([0-9]{2}:){2}[0-9]{2} \\+[0-9]{4}' then to_timestamp_tz({{timestamp_column}}, 'YYYY-MM-DDTHH24:MI:SSTZHTZM')
        when {{timestamp_column}} regexp '[0-9]{4}-[0-9]{2}-[0-9]{2}T([0-9]{2}:){2}[0-9]{2} \\+[0-9]{1,2}' then to_timestamp_tz({{timestamp_column}}, 'YYYY-MM-DDTHH24:MI:SS TZH')
        when {{timestamp_column}} regexp ('[0-9]{4}-[0-9]{2}-[0-9]{2}T([0-9]{2}:){2}[0-9]{2} UTC') then to_timestamp_tz({{timestamp_column}} || '+0', 'YYYY-MM-DDTHH24:MI:SS UTC TZH')

        when {{timestamp_column}} regexp '[0-9]{4}-[0-9]{2}-[0-9]{2}T([0-9]{2}:){2}[0-9]{2}\\+[0-9]{4}' then to_timestamp_tz({{timestamp_column}}, 'YYYY-MM-DDTHH24:MI:SSTZHTZM')
        when {{timestamp_column}} regexp '[0-9]{4}-[0-9]{2}-[0-9]{2}T([0-9]{2}:){2}[0-9]{2}\\+[0-9]{1,2}' then to_timestamp_tz({{timestamp_column}}, 'YYYY-MM-DDTHH24:MI:SSTZH')
        when {{timestamp_column}} regexp '[0-9]{4}-[0-9]{2}-[0-9]{2}T([0-9]{2}:){2}[0-9]{2}UTC' then to_timestamp_tz({{timestamp_column}} || '+0', 'YYYY-MM-DDTHH24:MI:SSUTCTZH')
        else to_timestamp_tz({{timestamp_column}})
    end as {{timestamp_column}}
{% endmacro %}


{# date  -------------------------------------------------     #}

{%- macro type_date() -%}
  {{ adapter.dispatch('type_date')() }}
{%- endmacro -%}

{% macro default__type_date() %}
    date
{% endmacro %}

{% macro oracle__type_date() %}
    varchar2(4000)
{% endmacro %}
