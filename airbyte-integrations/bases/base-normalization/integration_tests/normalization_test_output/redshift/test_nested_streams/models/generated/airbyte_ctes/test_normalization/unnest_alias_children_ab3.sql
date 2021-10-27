{{ config(schema="_airbyte_test_normalization", tags=["nested-intermediate"]) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        '_airbyte_unnest_alias_hashid',
        'ab_id',
        'owner',
    ]) }} as _airbyte_children_hashid,
    tmp.*
from {{ ref('unnest_alias_children_ab2') }} tmp
-- children at unnest_alias/children

