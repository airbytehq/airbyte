{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        quote('_AIRBYTE_CHILDREN_HASHID'),
        'owner_id',
    ]) }} as {{ quote('_AIRBYTE_OWNER_HASHID') }},
    tmp.*
from {{ ref('unnest_alias_children_owner_ab2') }} tmp
-- owner at unnest_alias/children/owner

