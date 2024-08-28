{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = '_AIRBYTE_AB_ID',
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('DEDUP_EXCHANGE_RATE_AB1') }}
select
    cast(ID as {{ dbt_utils.type_bigint() }}) as ID,
    cast(CURRENCY as {{ dbt_utils.type_string() }}) as CURRENCY,
    cast({{ empty_string_to_null('DATE') }} as {{ type_date() }}) as DATE,
    case
        when TIMESTAMP_COL regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{4}' then to_timestamp_tz(TIMESTAMP_COL, 'YYYY-MM-DDTHH24:MI:SSTZHTZM')
        when TIMESTAMP_COL regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}(\\+|-)\\d{2}' then to_timestamp_tz(TIMESTAMP_COL, 'YYYY-MM-DDTHH24:MI:SSTZH')
        when TIMESTAMP_COL regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{4}' then to_timestamp_tz(TIMESTAMP_COL, 'YYYY-MM-DDTHH24:MI:SS.FFTZHTZM')
        when TIMESTAMP_COL regexp '\\d{4}-\\d{2}-\\d{2}T(\\d{2}:){2}\\d{2}\\.\\d{1,7}(\\+|-)\\d{2}' then to_timestamp_tz(TIMESTAMP_COL, 'YYYY-MM-DDTHH24:MI:SS.FFTZH')
        when TIMESTAMP_COL = '' then NULL
    else to_timestamp_tz(TIMESTAMP_COL)
    end as TIMESTAMP_COL
    ,
    cast({{ adapter.quote('HKD@spéçiäl & characters') }} as {{ dbt_utils.type_float() }}) as {{ adapter.quote('HKD@spéçiäl & characters') }},
    cast(HKD_SPECIAL___CHARACTERS as {{ dbt_utils.type_string() }}) as HKD_SPECIAL___CHARACTERS,
    cast(NZD as {{ dbt_utils.type_float() }}) as NZD,
    cast(USD as {{ dbt_utils.type_float() }}) as USD,
    _AIRBYTE_AB_ID,
    _AIRBYTE_EMITTED_AT,
    {{ current_timestamp() }} as _AIRBYTE_NORMALIZED_AT
from {{ ref('DEDUP_EXCHANGE_RATE_AB1') }}
-- DEDUP_EXCHANGE_RATE
where 1 = 1
{{ incremental_clause('_AIRBYTE_EMITTED_AT', this) }}

