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
        '_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid',
        array_to_string('double_array_data'),
        array_to_string('DATA'),
        array_to_string('column___with__quotes'),
    ]) }} as _airbyte_partition_hashid,
    tmp.*
from {{ ref('nested_stream_with_complex_columns_resulting_into_long_names_partition_ab2') }} tmp
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1

