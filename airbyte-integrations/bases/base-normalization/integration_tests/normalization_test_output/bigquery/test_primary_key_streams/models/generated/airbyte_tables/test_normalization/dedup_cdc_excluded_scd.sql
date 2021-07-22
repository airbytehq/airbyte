{{ config(schema="test_normalization", tags=["top-level"]) }}
-- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
select
    id,
    name,
    _ab_cdc_lsn,
    _ab_cdc_updated_at,
    _ab_cdc_deleted_at,
    _airbyte_emitted_at as _airbyte_start_at,
    lag(_airbyte_emitted_at) over (
        partition by id
        order by _airbyte_emitted_at is null asc, _airbyte_emitted_at desc, _airbyte_emitted_at desc
    ) as _airbyte_end_at,
    lag(_airbyte_emitted_at) over (
        partition by id
        order by _airbyte_emitted_at is null asc, _airbyte_emitted_at desc, _airbyte_emitted_at desc, _ab_cdc_updated_at desc
    ) is null and _ab_cdc_deleted_at is null as _airbyte_active_row,
    _airbyte_emitted_at,
    _airbyte_dedup_cdc_excluded_hashid
from {{ ref('dedup_cdc_excluded_ab4') }}
-- dedup_cdc_excluded from {{ source('test_normalization', '_airbyte_raw_dedup_cdc_excluded') }}
where _airbyte_row_num = 1

