{{ config(schema="test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as {{ dbt_utils.type_bigint() }}) as id,
    cast(name as {{ dbt_utils.type_string() }}) as name,
    cast({{ quote('_AB_CDC_LSN') }} as {{ dbt_utils.type_float() }}) as {{ quote('_AB_CDC_LSN') }},
    cast({{ quote('_AB_CDC_UPDATED_AT') }} as {{ dbt_utils.type_float() }}) as {{ quote('_AB_CDC_UPDATED_AT') }},
    cast({{ quote('_AB_CDC_DELETED_AT') }} as {{ dbt_utils.type_float() }}) as {{ quote('_AB_CDC_DELETED_AT') }},
    cast({{ quote('_AB_CDC_LOG_POS') }} as {{ dbt_utils.type_float() }}) as {{ quote('_AB_CDC_LOG_POS') }},
    {{ quote('_AIRBYTE_EMITTED_AT') }}
from {{ ref('pos_dedup_cdcx_ab1') }}
-- pos_dedup_cdcx

