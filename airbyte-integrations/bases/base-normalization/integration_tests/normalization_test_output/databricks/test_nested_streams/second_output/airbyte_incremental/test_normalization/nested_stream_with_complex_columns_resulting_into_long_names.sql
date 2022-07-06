
    
  
  
    merge into test_normalization.nested_stream_with_complex_columns_resulting_into_long_names as DBT_INTERNAL_DEST
      using nested_stream_with_complex_columns_resulting_into_long_names__dbt_tmp as DBT_INTERNAL_SOURCE
      
      
    
        on DBT_INTERNAL_SOURCE._airbyte_unique_key = DBT_INTERNAL_DEST._airbyte_unique_key
    
  
      
      when matched then update set
         * 
    
      when not matched then insert *
