
  create view "postgres"._airbyte_test_normalization."pos_dedup_cdcx_ab3__dbt_tmp" as (
    
-- SQL model to build a hash column based on the values of this record
select
    md5(cast(coalesce(cast("id" as 
    varchar
), '') || '-' || coalesce(cast("name" as 
    varchar
), '') || '-' || coalesce(cast(_ab_cdc_lsn as 
    varchar
), '') || '-' || coalesce(cast(_ab_cdc_updated_at as 
    varchar
), '') || '-' || coalesce(cast(_ab_cdc_deleted_at as 
    varchar
), '') || '-' || coalesce(cast(_ab_cdc_log_pos as 
    varchar
), '') as 
    varchar
)) as _airbyte_pos_dedup_cdcx_hashid,
    tmp.*
from "postgres"._airbyte_test_normalization."pos_dedup_cdcx_ab2" tmp
-- pos_dedup_cdcx
  );
