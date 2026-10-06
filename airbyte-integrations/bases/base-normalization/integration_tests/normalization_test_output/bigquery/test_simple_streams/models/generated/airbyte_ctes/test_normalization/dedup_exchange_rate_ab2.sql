{{ config(
    cluster_by = "_airbyte_emitted_at",
    partition_by = {"field": "_airbyte_emitted_at", "data_type": "timestamp", "granularity": "day"},
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
-- depends_on: {{ ref('dedup_exchange_rate_ab1') }}
select
    cast(id as {{ dbt_utils.type_bigint() }}) as id,
    cast(currency as {{ dbt_utils.type_string() }}) as currency,
    cast({{ empty_string_to_null('date') }} as {{ type_date() }}) as date,
    cast({{ empty_string_to_null('timestamp_col') }} as {{ type_timestamp_with_timezone() }}) as timestamp_col,
    cast(HKD_special___characters as {{ dbt_utils.type_float() }}) as HKD_special___characters,
    cast(HKD_special___characters_1 as {{ dbt_utils.type_string() }}) as HKD_special___characters_1,
    cast(NZD as {{ dbt_utils.type_float() }}) as NZD,
    cast(USD as {{ dbt_utils.type_float() }}) as USD,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at
from {{ ref('dedup_exchange_rate_ab1') }}
-- dedup_exchange_rate
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

