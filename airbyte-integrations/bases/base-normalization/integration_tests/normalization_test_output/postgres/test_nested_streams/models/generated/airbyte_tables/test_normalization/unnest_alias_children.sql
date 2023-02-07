{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "test_normalization",
    post_hook = ["
                    {%
                        set scd_table_relation = adapter.get_relation(
                            database=this.database,
                            schema=this.schema,
                            identifier='unnest_alias_children_scd'
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
-- depends_on: {{ ref('unnest_alias_children_ab3') }}
select
    _airbyte_unnest_alias_hashid,
    ab_id,
    {{ adapter.quote('owner') }},
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_children_hashid
from {{ ref('unnest_alias_children_ab3') }}
-- children at unnest_alias/children from {{ ref('unnest_alias') }}
where 1 = 1

