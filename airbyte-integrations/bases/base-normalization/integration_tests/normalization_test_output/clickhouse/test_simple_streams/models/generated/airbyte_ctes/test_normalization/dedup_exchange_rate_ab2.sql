{{ config(
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('dedup_exchange_rate_ab1') }}
select
    accurateCastOrNull(trim(BOTH '"' from id), '{{ dbt_utils.type_bigint() }}') as id,
    nullif(accurateCastOrNull(trim(BOTH '"' from currency), '{{ dbt_utils.type_string() }}'), 'null') as currency,
    toDate(parseDateTimeBestEffortOrNull(trim(BOTH '"' from {{ empty_string_to_null('date') }}))) as date,
    parseDateTime64BestEffortOrNull(trim(BOTH '"' from {{ empty_string_to_null('timestamp_col') }})) as timestamp_col,
    accurateCastOrNull(trim(BOTH '"' from {{ quote('HKD@spéçiäl & characters') }}), '{{ dbt_utils.type_float() }}') as {{ quote('HKD@spéçiäl & characters') }},
    nullif(accurateCastOrNull(trim(BOTH '"' from HKD_special___characters), '{{ dbt_utils.type_string() }}'), 'null') as HKD_special___characters,
    accurateCastOrNull(trim(BOTH '"' from NZD), '{{ dbt_utils.type_float() }}') as NZD,
    accurateCastOrNull(trim(BOTH '"' from USD), '{{ dbt_utils.type_float() }}') as USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('dedup_exchange_rate_ab1') }}
-- dedup_exchange_rate
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

