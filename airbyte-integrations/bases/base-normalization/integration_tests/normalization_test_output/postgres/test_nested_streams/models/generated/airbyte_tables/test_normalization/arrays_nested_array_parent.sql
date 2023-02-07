{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "test_normalization",
    post_hook = ["
                    {%
                        set scd_table_relation = adapter.get_relation(
                            database=this.database,
                            schema=this.schema,
                            identifier='arrays_nested_array_parent_scd'
                        )
                    %}
                    {%
                        if scd_table_relation is not none
                    %}
                    {%
                            do adapter.drop_relation(scd_table_relation)
                    %}
                    {% endif %}
                        "],
    tags = [ "nested" ]
) }}
-- Final base SQL model
-- depends_on: {{ ref('arrays_nested_array_parent_ab3') }}
select
    _airbyte_arrays_hashid,
    nested_array,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_nested_array_parent_hashid
from {{ ref('arrays_nested_array_parent_ab3') }}
-- nested_array_parent at arrays/nested_array_parent from {{ ref('arrays') }}
where 1 = 1

