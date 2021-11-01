
  create view _airbyte_test_normalization.`pos_dedup_cdcx_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(id as char), ''), '-', coalesce(cast(`name` as char), ''), '-', coalesce(cast(_ab_cdc_lsn as char), ''), '-', coalesce(cast(_ab_cdc_updated_at as char), ''), '-', coalesce(cast(_ab_cdc_deleted_at as char), ''), '-', coalesce(cast(_ab_cdc_log_pos as char), '')) as char)) as _airbyte_pos_dedup_cdcx_hashid,
    tmp.*
from _airbyte_test_normalization.`pos_dedup_cdcx_ab2` tmp
-- pos_dedup_cdcx
where 1 = 1
  );
