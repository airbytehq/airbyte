{# json  -------------------------------------------------     #}

{%- macro type_json() -%}
  {{ adapter.dispatch('type_json')() }}
{%- endmacro -%}

{% macro default__type_json() %}
    string
{% endmacro %}

{%- macro redshift__type_json() -%}
  {%- if redshift_super_type() -%}
    super
  {%- else -%}
    varchar
  {%- endif -%}
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

{%- macro sqlserver__type_json() -%}
    NVARCHAR(max)
{%- endmacro -%}

{% macro clickhouse__type_json() %}
    String
{% endmacro %}


{# string ------------------------------------------------- #}

{%- macro mysql__type_string() -%}
    char
{%- endmacro -%}

{%- macro oracle__type_string() -%}
    varchar2(4000)
{%- endmacro -%}

{% macro sqlserver__type_string() %}
    NVARCHAR(max)
{%- endmacro -%}

{%- macro clickhouse__type_string() -%}
    String
{%- endmacro -%}


{# float ------------------------------------------------- #}
{% macro mysql__type_float() %}
    float
{% endmacro %}

{% macro oracle__type_float() %}
    float
{% endmacro %}

{% macro clickhouse__type_float() %}
    Float64
{% endmacro %}


{# int  ------------------------------------------------- #}
{% macro default__type_int() %}
    signed
{% endmacro %}

{% macro oracle__type_int() %}
    int
{% endmacro %}

{% macro clickhouse__type_int() %}
    INT
{% endmacro %}


{# bigint ------------------------------------------------- #}
{% macro mysql__type_bigint() %}
    signed
{% endmacro %}

{% macro oracle__type_bigint() %}
    numeric
{% endmacro %}

{% macro clickhouse__type_bigint() %}
    BIGINT
{% endmacro %}


{# numeric ------------------------------------------------- --#}
{% macro mysql__type_numeric() %}
    float
{% endmacro %}

{% macro clickhouse__type_numeric() %}
    Float64
{% endmacro %}


{# timestamp ------------------------------------------------- --#}
{% macro mysql__type_timestamp() %}
    time
{% endmacro %}

{%- macro sqlserver__type_timestamp() -%}
    {#-- in TSQL timestamp is really datetime --#}
    {#-- https://docs.microsoft.com/en-us/sql/t-sql/functions/date-and-time-data-types-and-functions-transact-sql?view=sql-server-ver15#DateandTimeDataTypes --#}
    datetime
{%- endmacro -%}

{% macro clickhouse__type_timestamp() %}
    DateTime64
{% endmacro %}


{# timestamp with time zone  -------------------------------------------------     #}

{%- macro type_timestamp_with_timezone() -%}
  {{ adapter.dispatch('type_timestamp_with_timezone')() }}
{%- endmacro -%}

{% macro default__type_timestamp_with_timezone() %}
    timestamp with time zone
{% endmacro %}

{% macro bigquery__type_timestamp_with_timezone() %}
    timestamp
{% endmacro %}

{#-- MySQL doesnt allow cast operation to work with TIMESTAMP so we have to use char --#}
{%- macro mysql__type_timestamp_with_timezone() -%}
    char
{%- endmacro -%}

{% macro oracle__type_timestamp_with_timezone() %}
    varchar2(4000)
{% endmacro %}

{%- macro sqlserver__type_timestamp_with_timezone() -%}
    {#-- in TSQL timestamp is really datetime or datetime2 --#}
    {#-- https://docs.microsoft.com/en-us/sql/t-sql/functions/date-and-time-data-types-and-functions-transact-sql?view=sql-server-ver15#DateandTimeDataTypes --#}
    datetime2
{%- endmacro -%}

{% macro clickhouse__type_timestamp_with_timezone() %}
    DateTime64
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

{%- macro sqlserver__type_date() -%}
    date
{%- endmacro -%}

{% macro clickhouse__type_date() %}
    Date
{% endmacro %}
