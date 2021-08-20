

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_ab3`
  OPTIONS()
  as 
-- SQL model to build a hash column based on the values of this record
select
    *,
    to_hex(md5(cast(concat(coalesce(cast(id as 
    string
), ''), '-', coalesce(cast(array_to_string(children, "|", "") as 
    string
), '')) as 
    string
))) as _airbyte_unnest_alias_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`unnest_alias_ab2`
-- unnest_alias;

