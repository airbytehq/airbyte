{{ config(
    cluster_by = "_airbyte_emitted_at",
    partition_by = {"field": "_airbyte_emitted_at", "data_type": "timestamp", "granularity": "day"},
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_airbyte_ab_id'),
    schema = "test_normalization",
    tags = [ "top-level" ]
) }}
-- Final base SQL model
select
    id,
    currency,
    date,
    timestamp_col,
    HKD_special___characters,
    HKD_special___characters_1,
    NZD,
    USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_exchange_rate_hashid
from {{ ref('exchange_rate_ab3') }}
-- exchange_rate from {{ source('test_normalization', '_airbyte_raw_exchange_rate') }}
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at') }}

