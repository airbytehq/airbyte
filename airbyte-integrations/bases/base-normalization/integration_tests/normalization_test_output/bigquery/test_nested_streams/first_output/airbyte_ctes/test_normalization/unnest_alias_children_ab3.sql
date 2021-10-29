

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_children_ab3`
  OPTIONS()
  as 
-- SQL model to build a hash column based on the values of this record
select
    to_hex(md5(cast(concat(coalesce(cast(_airbyte_unnest_alias_hashid as 
    string
), ''), '-', coalesce(cast(ab_id as 
    string
), ''), '-', coalesce(cast(owner as 
    string
), '')) as 
    string
))) as _airbyte_children_hashid,
    tmp.*
from `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_children_ab2` tmp
-- children at unnest_alias/children
where 1 = 1;

