
        
    

    

    merge into `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA` as DBT_INTERNAL_DEST
        using (
          select * from `dataline-integration-testing`.test_normalization.`nested_stream_with_complex_columns_resulting_into_long_names_partition_DATA__dbt_tmp`
        ) as DBT_INTERNAL_SOURCE
        on FALSE

    

    when not matched then insert
        (`_airbyte_partition_hashid`, `currency`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_DATA_hashid`)
    values
        (`_airbyte_partition_hashid`, `currency`, `_airbyte_ab_id`, `_airbyte_emitted_at`, `_airbyte_normalized_at`, `_airbyte_DATA_hashid`)


  