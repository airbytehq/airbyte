{{ config(schema="_AIRBYTE_TEST_NORMALIZATION", tags=["top-level-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'ID',
        'NAME',
        '_AB_CDC_LSN',
        '_AB_CDC_UPDATED_AT',
        '_AB_CDC_DELETED_AT',
    ]) }} as _AIRBYTE_DEDUP_CDC_EXCLUDED_HASHID,
    tmp.*
from {{ ref('DEDUP_CDC_EXCLUDED_AB2') }} tmp
-- DEDUP_CDC_EXCLUDED

