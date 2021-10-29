

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`pos_dedup_cdcx_ab3`
  OPTIONS()
  as 
-- SQL model to build a hash column based on the values of this record
select
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
), ''), '-', coalesce(cast(_ab_cdc_log_pos as 
    string
), '')) as 
    string
))) as _airbyte_pos_dedup_cdcx_hashid,
    tmp.*
from `dataline-integration-testing`._airbyte_test_normalization.`pos_dedup_cdcx_ab2` tmp
-- pos_dedup_cdcx
where 1 = 1;

