{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as {{ dbt_utils.type_bigint() }}) as id,
    cast({{ adapter.quote('name') }} as {{ dbt_utils.type_string() }}) as {{ adapter.quote('name') }},
    cast(_ab_cdc_lsn as {{ dbt_utils.type_float() }}) as _ab_cdc_lsn,
    cast(_ab_cdc_updated_at as {{ dbt_utils.type_float() }}) as _ab_cdc_updated_at,
    cast(_ab_cdc_deleted_at as {{ dbt_utils.type_float() }}) as _ab_cdc_deleted_at,
    cast(_ab_cdc_log_pos as {{ dbt_utils.type_float() }}) as _ab_cdc_log_pos,
    _airbyte_emitted_at
from {{ ref('pos_dedup_cdcx_ab1') }}
-- pos_dedup_cdcx

