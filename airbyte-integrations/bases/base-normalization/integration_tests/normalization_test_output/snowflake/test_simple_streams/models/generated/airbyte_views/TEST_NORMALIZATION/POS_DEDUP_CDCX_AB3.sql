{{ config(
    cluster_by = ["_AIRBYTE_EMITTED_AT"],
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_AIRBYTE_AB_ID'),
    schema = "_AIRBYTE_TEST_NORMALIZATION",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'ID',
        'NAME',
        '_AB_CDC_LSN',
        '_AB_CDC_UPDATED_AT',
        '_AB_CDC_DELETED_AT',
        '_AB_CDC_LOG_POS',
    ]) }} as _AIRBYTE_POS_DEDUP_CDCX_HASHID,
    tmp.*
from {{ ref('POS_DEDUP_CDCX_AB2') }} tmp
-- POS_DEDUP_CDCX
where 1 = 1

