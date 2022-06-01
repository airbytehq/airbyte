

  create view "integrationtests"._airbyte_test_normalization."nested_stream_with_complex_columns_resulting_into_long_names_scd_new_data__dbt_tmp" as (
    
-- depends_on: ref('nested_stream_with_complex_columns_resulting_into_long_names_stg')

select * from "integrationtests"._airbyte_test_normalization."nested_stream_with_complex_columns_resulting_into_long_names_stg"


  ) ;
