{{ config(
    indexes = [{'columns':['_airbyte_emitted_at'],'type':'btree'}],
    schema = "test_normalization",
    post_hook = ["
                    {%
                        set scd_table_relation = adapter.get_relation(
                            database=this.database,
                            schema=this.schema,
                            identifier='unnest_alias_childre__column___with__quotes_scd'
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
-- depends_on: {{ ref('unnest_alias_childre__column___with__quotes_ab3') }}
select
    _airbyte_owner_hashid,
    currency,
    _airbyte_ab_id,
    _airbyte_emitted_at,
    {{ current_timestamp() }} as _airbyte_normalized_at,
    _airbyte_column___with__quotes_hashid
from {{ ref('unnest_alias_childre__column___with__quotes_ab3') }}
-- column___with__quotes at unnest_alias/children/owner/column`_'with"_quotes from {{ ref('unnest_alias_children_owner') }}
where 1 = 1

