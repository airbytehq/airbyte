{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "_airbyte_test_normalization",
    tags = [ "nested-intermediate" ]
) }}
-- SQL model to build a hash column based on the values of this record
-- depends_on: {{ ref('nested_stream_with_c___long_names_partition_ab2') }}
select
    {{ dbt_utils.surrogate_key([
        '_airbyte_nested_stre__nto_long_names_hashid',
        array_to_string('double_array_data'),
        array_to_string(adapter.quote('DATA')),
    ]) }} as _airbyte_partition_hashid,
    tmp.*
from {{ ref('nested_stream_with_c___long_names_partition_ab2') }} tmp
-- partition at nested_stream_with_complex_columns_resulting_into_long_names/partition
where 1 = 1
{{ incremental_clause('_airbyte_emitted_at', this) }}

