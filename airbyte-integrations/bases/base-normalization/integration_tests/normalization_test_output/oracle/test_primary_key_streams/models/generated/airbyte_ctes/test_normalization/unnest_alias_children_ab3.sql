{{ config(schema="test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        quote('_AIRBYTE_UNNEST_ALIAS_HASHID'),
        'ab_id',
        'owner',
    ]) }} as {{ quote('_AIRBYTE_CHILDREN_HASHID') }},
    tmp.*
from {{ ref('unnest_alias_children_ab2') }} tmp
-- children at unnest_alias/children

