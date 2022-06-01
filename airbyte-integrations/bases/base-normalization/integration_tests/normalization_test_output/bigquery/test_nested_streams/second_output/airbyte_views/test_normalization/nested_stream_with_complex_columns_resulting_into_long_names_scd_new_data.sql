

  create or replace view `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_scd_new_data`
  OPTIONS()
  as 
-- depends_on: ref('nested_stream_with_complex_columns_resulting_into_long_names_stg')

select * from `dataline-integration-testing`._airbyte_test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_stg`

;

