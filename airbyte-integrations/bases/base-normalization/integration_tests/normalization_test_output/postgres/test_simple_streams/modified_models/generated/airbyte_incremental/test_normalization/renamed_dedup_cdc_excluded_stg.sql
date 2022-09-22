{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    unique_key = '_airbyte_ab_id',
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('renamed_dedup_cdc_excluded_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        adapter.quote('id'),
        adapter.quote('name'),
        '_ab_cdc_lsn',
        '_ab_cdc_updated_at',
        '_ab_cdc_deleted_at',
    ]) }} as _airbyte_renamed_dedup_cdc_excluded_hashid,
    tmp.*
from {{ ref('renamed_dedup_cdc_excluded_ab2') }} tmp
-- renamed_dedup_cdc_excluded
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

