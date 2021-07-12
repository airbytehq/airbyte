{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as {{ dbt_utils.type_bigint() }}) as id,
    cast(name as {{ dbt_utils.type_string() }}) as name,
    cast(_ab_cdc_lsn as {{ dbt_utils.type_float() }}) as _ab_cdc_lsn,
    cast(_ab_cdc_updated_at as {{ dbt_utils.type_float() }}) as _ab_cdc_updated_at,
    cast(_ab_cdc_deleted_at as {{ dbt_utils.type_float() }}) as _ab_cdc_deleted_at,
    _airbyte_emitted_at
from {{ ref('dedup_cdc_excluded_ab1') }}
-- dedup_cdc_excluded

