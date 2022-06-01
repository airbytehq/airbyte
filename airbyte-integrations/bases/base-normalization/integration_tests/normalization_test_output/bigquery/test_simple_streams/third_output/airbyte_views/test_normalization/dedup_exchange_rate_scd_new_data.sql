

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`dedup_exchange_rate_scd_new_data`
  OPTIONS()
  as 
-- depends_on: ref('dedup_exchange_rate_stg')

select * from `dataline-integration-testing`._airbyte_test_normalization.`dedup_exchange_rate_stg`

;

