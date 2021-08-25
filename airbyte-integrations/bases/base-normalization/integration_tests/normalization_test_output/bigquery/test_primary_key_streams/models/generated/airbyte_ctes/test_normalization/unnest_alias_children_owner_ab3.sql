{{ config(schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    *,
    {{ dbt_utils.surrogate_key([
        '_airbyte_children_hashid',
        'owner_id',
    ]) }} as _airbyte_owner_hashid
from {{ ref('unnest_alias_children_owner_ab2') }}
-- owner at unnest_alias/children/owner

