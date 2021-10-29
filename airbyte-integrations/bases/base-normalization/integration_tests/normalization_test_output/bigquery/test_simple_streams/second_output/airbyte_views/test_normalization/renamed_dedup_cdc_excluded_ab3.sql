

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`renamed_dedup_cdc_excluded_ab3`
  OPTIONS()
  as 
-- SQL model to build a hash column based on the values of this record
select
    to_hex(md5(cast(concat(coalesce(cast(id as 
    string
), '')) as 
    string
))) as _airbyte_renamed_dedup_cdc_excluded_hashid,
    tmp.*
from `dataline-integration-testing`._airbyte_test_normalization.`renamed_dedup_cdc_excluded_ab2` tmp
-- renamed_dedup_cdc_excluded
where 1 = 1
;

