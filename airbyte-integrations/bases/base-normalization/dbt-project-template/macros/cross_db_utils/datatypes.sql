{# json  -------------------------------------------------     #}

{%- macro type_json() -%}
  {{ adapter.dispatch('type_json')() }}
{%- endmacro -%}

{% macro default__type_json() %}
    string
{% endmacro %}

{%- macro type_binary() -%}
  {{ adapter.dispatch('type_binary')() }}
{%- endmacro -%}

{%- macro default__type_binary() -%}
    binary
{%- endmacro -%}

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

{%- macro tidb__type_json() -%}
    json
{%- endmacro -%}


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

{#-- TODO: Remove this macro when dbt issue regarding unlimited varchars on postgres is resolved (https://github.com/dbt-labs/dbt-core/issues/5238) and we've upgraded to the latest version of dbt --#}
{%- macro postgres__type_string() -%}
    text
{%- endmacro -%}

{%- macro tidb__type_string() -%}
    char(1000)
{%- endmacro -%}

{# binary data ------------------------------------------------- #}

{%- macro postgres__type_binary() -%}
    bytea
{%- endmacro -%}

{%- macro bigquery__type_binary() -%}
    bytes
{%- endmacro -%}

{%- macro mssql__type_binary() -%}
    VARBINARY(MAX)
{%- endmacro -%}

{%- macro snowflake__type_binary() -%}
    VARBINARY
{%- endmacro -%}

{%- macro clickhouse__type_binary() -%}
    VARBINARY
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

{% macro tidb__type_float() %}
    float
{% endmacro %}

{# int  ------------------------------------------------- #}
{% macro default__type_int() %}
    int
{% endmacro %}

{% macro mysql__type_int() %}
    signed
{% endmacro %}

{% macro oracle__type_int() %}
    int
{% endmacro %}

{% macro clickhouse__type_int() %}
    INT
{% endmacro %}

{% macro tidb__type_int() %}
    signed
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

{% macro tidb__type_bigint() %}
    signed
{% endmacro %}

{# numeric ------------------------------------------------- --#}
{% macro mysql__type_numeric() %}
    float
{% endmacro %}

{% macro clickhouse__type_numeric() %}
    Float64
{% endmacro %}

{% macro tidb__type_numeric() %}
    float
{% endmacro %}

{# very_large_integer --------------------------------------- --#}
{#
Most databases don't have a true unbounded numeric datatype, so we use a really big numeric field.
Our type terminology unfortunately collides with DB terminology (i.e. "big_integer" means different things in different contexts)
so this macro needs to be called very_large_integer.
#}
{%- macro type_very_large_integer() -%}
  {{ adapter.dispatch('type_very_large_integer')() }}
{%- endmacro -%}

{% macro default__type_very_large_integer() %}
    numeric
{% endmacro %}

{% macro snowflake__type_very_large_integer() %}
    numeric
{% endmacro %}

{% macro mysql__type_very_large_integer() %}
    decimal(38, 0)
{% endmacro %}

{% macro clickhouse__type_very_large_integer() %}
    decimal128(0)
{% endmacro %}

{% macro tidb__type_very_large_integer() %}
    decimal(38, 0)
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

{% macro tidb__type_timestamp() %}
    time
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

{#-- MySQL doesnt allow cast operation with nullif to work with DATETIME and doesn't support storing of timezone so we have to use char --#}
{#-- https://bugs.mysql.com/bug.php?id=77805 --#}
{%- macro mysql__type_timestamp_with_timezone() -%}
    char(1024)
{%- endmacro -%}

{% macro oracle__type_timestamp_with_timezone() %}
    varchar2(4000)
{% endmacro %}

{%- macro sqlserver__type_timestamp_with_timezone() -%}
    datetimeoffset
{%- endmacro -%}

{% macro redshift__type_timestamp_with_timezone() %}
    TIMESTAMPTZ
{% endmacro %}

{% macro clickhouse__type_timestamp_with_timezone() %}
    DateTime64
{% endmacro %}

{%- macro tidb__type_timestamp_with_timezone() -%}
    char(1000)
{%- endmacro -%}

{# timestamp without time zone  -------------------------------------------------     #}

{%- macro type_timestamp_without_timezone() -%}
  {{ adapter.dispatch('type_timestamp_without_timezone')() }}
{%- endmacro -%}

{% macro default__type_timestamp_without_timezone() %}
    timestamp
{% endmacro %}

{%- macro sqlserver__type_timestamp_without_timezone() -%}
    {#-- in TSQL timestamp is really datetime or datetime2 --#}
    {#-- https://docs.microsoft.com/en-us/sql/t-sql/functions/date-and-time-data-types-and-functions-transact-sql?view=sql-server-ver15#DateandTimeDataTypes --#}
    datetime2
{%- endmacro -%}

{% macro bigquery__type_timestamp_without_timezone() %}
    datetime
{% endmacro %}

{% macro oracle__type_timestamp_without_timezone() %}
    varchar2(4000)
{% endmacro %}

{% macro redshift__type_timestamp_without_timezone() %}
    TIMESTAMP
{% endmacro %}

{% macro tidb__type_timestamp_without_timezone() %}
    datetime
{% endmacro %}

{# time without time zone  -------------------------------------------------     #}

{%- macro type_time_without_timezone() -%}
  {{ adapter.dispatch('type_time_without_timezone')() }}
{%- endmacro -%}

{% macro default__type_time_without_timezone() %}
    time
{% endmacro %}

{% macro oracle__type_time_without_timezone() %}
    varchar2(4000)
{% endmacro %}

{% macro redshift__type_time_without_timezone() %}
    TIME
{% endmacro %}

{% macro clickhouse__type_time_without_timezone() %}
    String
{% endmacro %}

{% macro tidb__type_time_without_timezone() %}
    time
{% endmacro %}


{# time with time zone  -------------------------------------------------     #}

{%- macro type_time_with_timezone() -%}
  {{ adapter.dispatch('type_time_with_timezone')() }}
{%- endmacro -%}

{% macro default__type_time_with_timezone() %}
    time with time zone
{% endmacro %}

{%- macro mysql__type_time_with_timezone() -%}
    char(1024)
{%- endmacro -%}

{%- macro sqlserver__type_time_with_timezone() -%}
    NVARCHAR(max)
{%- endmacro -%}

{% macro bigquery__type_time_with_timezone() %}
    STRING
{% endmacro %}

{% macro oracle__type_time_with_timezone() %}
    varchar2(4000)
{% endmacro %}

{% macro snowflake__type_time_with_timezone() %}
    varchar
{% endmacro %}

{% macro redshift__type_time_with_timezone() %}
    TIMETZ
{% endmacro %}

{% macro clickhouse__type_time_with_timezone() %}
    String
{% endmacro %}

{%- macro tidb__type_time_with_timezone() -%}
    char(1000)
{%- endmacro -%}

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
    Date32
{% endmacro %}
