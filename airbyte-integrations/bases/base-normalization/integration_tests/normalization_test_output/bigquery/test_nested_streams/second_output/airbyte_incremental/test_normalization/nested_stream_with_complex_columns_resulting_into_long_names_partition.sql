
        
        
    

    

    merge into `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition` as DBT_INTERNAL_DEST
        using (
          select * from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition__dbt_tmp`
        ) as DBT_INTERNAL_SOURCE
        on 
            DBT_INTERNAL_SOURCE._airbyte_ab_id = DBT_INTERNAL_DEST._airbyte_ab_id
        

    
    when matched then update set
        `_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid` = DBT_INTERNAL_SOURCE.`_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid`,`double_array_data` = DBT_INTERNAL_SOURCE.`double_array_data`,`DATA` = DBT_INTERNAL_SOURCE.`DATA`,`_airbyte_ab_id` = DBT_INTERNAL_SOURCE.`_airbyte_ab_id`,`_airbyte_emitted_at` = DBT_INTERNAL_SOURCE.`_airbyte_emitted_at`,`_airbyte_normalized_at` = DBT_INTERNAL_SOURCE.`_airbyte_normalized_at`,`_airbyte_partition_hashid` = DBT_INTERNAL_SOURCE.`_airbyte_partition_hashid`
    

    when not matched then insert
        (`_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid`, `double_array_data`, `DATA`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_partition_hashid`)
    values
        (`_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid`, `double_array_data`, `DATA`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_partition_hashid`)


  