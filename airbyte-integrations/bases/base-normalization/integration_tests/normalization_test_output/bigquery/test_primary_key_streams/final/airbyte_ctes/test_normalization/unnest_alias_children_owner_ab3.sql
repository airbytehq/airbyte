

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_children_owner_ab3`
  OPTIONS()
  as 
-- SQL model to build a hash column based on the values of this record
select
    *,
    to_hex(md5(cast(concat(coalesce(cast(_airbyte_children_hashid as 
    string
), ''), '-', coalesce(cast(owner_id as 
    string
), '')) as 
    string
))) as _airbyte_owner_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_children_owner_ab2`
-- owner at unnest_alias/children/owner;

