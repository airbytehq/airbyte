
  create view test_normalization.dedup_exchange_rate_scd_new_data__dbt_tmp as
    
-- depends_on: ref('dedup_exchange_rate_stg')

select * from test_normalization.dedup_exchange_rate_stg



