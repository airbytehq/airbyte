

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`dedup_exchange_rate_ab3`
  OPTIONS()
  as 
-- SQL model to build a hash column based on the values of this record
select
    *,
    to_hex(md5(cast(concat(coalesce(cast(id as 
    string
), ''), '-', coalesce(cast(currency as 
    string
), ''), '-', coalesce(cast(date as 
    string
), ''), '-', coalesce(cast(timestamp_col as 
    string
), ''), '-', coalesce(cast(HKD_special___characters as 
    string
), ''), '-', coalesce(cast(HKD_special___characters_1 as 
    string
), ''), '-', coalesce(cast(NZD as 
    string
), ''), '-', coalesce(cast(USD as 
    string
), '')) as 
    string
))) as _airbyte_dedup_exchange_rate_hashid
from `dataline-integration-testing`._airbyte_test_normalization.`dedup_exchange_rate_ab2`
-- dedup_exchange_rate;

