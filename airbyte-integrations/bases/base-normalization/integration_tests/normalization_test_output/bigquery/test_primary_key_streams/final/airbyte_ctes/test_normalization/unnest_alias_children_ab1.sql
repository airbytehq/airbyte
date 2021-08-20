

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_children_ab1`
  OPTIONS()
  as 
-- SQL model to parse JSON blob stored in a single column and extract into separated field columns as described by the JSON Schema

select
    _airbyte_unnest_alias_hashid,
    json_extract_scalar(children, "$['ab_id']") as ab_id,
    
        json_extract(children, "$['owner']")
     as owner,
    _airbyte_emitted_at
from `dataline-integration-testing`.test_normalization.`unnest_alias` as table_alias
cross join unnest(children) as children
where children is not null
-- children at unnest_alias/children;

