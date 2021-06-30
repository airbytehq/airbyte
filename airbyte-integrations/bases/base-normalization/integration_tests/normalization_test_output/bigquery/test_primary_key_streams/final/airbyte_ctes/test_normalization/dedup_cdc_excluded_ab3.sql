

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`dedup_cdc_excluded_ab3`
  OPTIONS()
  as 
-- SQL model to build a hash column based on the values of this record
select
    *,
    to_hex(md5(cast(concat(coalesce(cast(id as 
    string
), ''), '-', coalesce(cast(name as 
    string
), ''), '-', coalesce(cast(_ab_cdc_lsn as 
    string
), ''), '-', coalesce(cast(_ab_cdc_updated_at as 
    string
), ''), '-', coalesce(cast(_ab_cdc_deleted_at as 
    string
), '')) as 
    string
))) as _airbyte_dedup_cdc_excluded_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`dedup_cdc_excluded_ab2`
-- dedup_cdc_excluded;

