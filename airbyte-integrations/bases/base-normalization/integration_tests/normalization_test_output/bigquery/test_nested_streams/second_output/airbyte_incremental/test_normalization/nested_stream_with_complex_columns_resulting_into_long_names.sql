
        
        
    

    

    merge into `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names` as DBT_INTERNAL_DEST
        using (
          select * from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names__dbt_tmp`
        ) as DBT_INTERNAL_SOURCE
        on 
            DBT_INTERNAL_SOURCE._airbyte_unique_key = DBT_INTERNAL_DEST._airbyte_unique_key
        

    
    when matched then update set
        `_airbyte_unique_key` = DBT_INTERNAL_SOURCE.`_airbyte_unique_key`,`id` = DBT_INTERNAL_SOURCE.`id`,`date` = DBT_INTERNAL_SOURCE.`date`,`partition` = DBT_INTERNAL_SOURCE.`partition`,`_airbyte_ab_id` = DBT_INTERNAL_SOURCE.`_airbyte_ab_id`,`_airbyte_emitted_at` = DBT_INTERNAL_SOURCE.`_airbyte_emitted_at`,`_airbyte_normalized_at` = DBT_INTERNAL_SOURCE.`_airbyte_normalized_at`,`_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid` = DBT_INTERNAL_SOURCE.`_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid`
    

    when not matched then insert
        (`_airbyte_unique_key`, `id`, `date`, `partition`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid`)
    values
        (`_airbyte_unique_key`, `id`, `date`, `partition`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_nested_stream_with_complex_columns_resulting_into_long_names_hashid`)


  