{{ config(
    cluster_by = "_airbyte_emitted_at",
    partition_by = {"field": "_airbyte_emitted_at", "data_type": "timestamp", "granularity": "day"},
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_airbyte_ab_id'),
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        '_airbyte_children_hashid',
        'owner_id',
    ]) }} as _airbyte_owner_hashid,
    tmp.*
from {{ ref('unnest_alias_children_owner_ab2') }} tmp
-- owner at unnest_alias/children/owner
where 1 = 1

