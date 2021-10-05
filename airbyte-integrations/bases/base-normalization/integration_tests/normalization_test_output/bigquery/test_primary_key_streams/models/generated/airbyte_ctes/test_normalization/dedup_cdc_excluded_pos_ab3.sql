{{ config(schema="_airbyte_test_normalization", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        'name',
        '_ab_cdc_lsn',
        '_ab_cdc_updated_at',
        '_ab_cdc_deleted_at',
        '_ab_cdc_log_pos',
    ]) }} as _airbyte_dedup_cdc_excluded_pos_hashid,
    tmp.*
from {{ ref('dedup_cdc_excluded_pos_ab2') }} tmp
-- dedup_cdc_excluded_pos

