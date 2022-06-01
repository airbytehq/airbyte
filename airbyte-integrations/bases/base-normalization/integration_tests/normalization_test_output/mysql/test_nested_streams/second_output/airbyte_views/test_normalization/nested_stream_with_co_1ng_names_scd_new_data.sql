
  create view _airbyte_test_normalization.`nested_stream_with_co_1ng_names_scd_new_data__dbt_tmp` as (
    
-- depends_on: ref('nested_stream_with_co_1g_into_long_names_stg')

select * from _airbyte_test_normalization.`nested_stream_with_co_1g_into_long_names_stg`


  );
