
    
  
  
    merge into test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data as DBT_INTERNAL_DEST
      using nested_stream_with_complex_columns_resulting_into_long_names_partition_double_array_data__dbt_tmp as DBT_INTERNAL_SOURCE
      
      
    
        on false
    
  
      
      when matched then update set
         * 
    
      when not matched then insert *
