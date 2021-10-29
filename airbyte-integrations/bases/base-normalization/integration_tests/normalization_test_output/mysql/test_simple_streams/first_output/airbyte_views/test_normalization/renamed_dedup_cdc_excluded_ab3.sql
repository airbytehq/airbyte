
  create view _airbyte_test_normalization.`renamed_dedup_cdc_excluded_ab3__dbt_tmp` as (
    
-- SQL model to build a hash column based on the values of this record
select
    md5(cast(concat(coalesce(cast(id as char), '')) as char)) as _airbyte_renamed_dedup_cdc_excluded_hashid,
    tmp.*
from _airbyte_test_normalization.`renamed_dedup_cdc_excluded_ab2` tmp
-- renamed_dedup_cdc_excluded
where 1 = 1

  );
