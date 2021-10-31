{{ config(
    cluster_by = "_airbyte_emitted_at",
    partition_by = {"field": "_airbyte_emitted_at", "data_type": "timestamp", "granularity": "day"},
    unique_key = env_var('AIRBYTE_DEFAULT_UNIQUE_KEY', '_airbyte_ab_id'),
    schema = "_airbyte_test_normalization_namespace",
    tags = [ "top-level-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
select
    {{ dbt_utils.surrogate_key([
        'id',
        'date',
    ]) }} as _airbyte_simple_stream_with_namespace_resulting_into_long_names_hashid,
    tmp.*
from {{ ref('simple_stream_with_namespace_resulting_into_long_names_ab2') }} tmp
-- simple_stream_with_namespace_resulting_into_long_names
where 1 = 1

