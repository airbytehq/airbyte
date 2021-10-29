{{ config(
    cluster_by = "_airbyte_emitted_at",
    partition_by = {"field": "_airbyte_emitted_at", "data_type": "timestamp", "granularity": "day"},
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_airbyte_ab_id'),
    schema = "_airbyte_test_normalization",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
    ]) }} as _airbyte_renamed_dedup_cdc_excluded_hashid,
    tmp.*
from {{ ref('renamed_dedup_cdc_excluded_ab2') }} tmp
-- renamed_dedup_cdc_excluded
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at') }}

