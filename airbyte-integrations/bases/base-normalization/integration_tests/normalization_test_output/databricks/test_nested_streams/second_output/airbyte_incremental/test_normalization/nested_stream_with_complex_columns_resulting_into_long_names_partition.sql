
    
  
  
    merge into test_normalization.nested_stream_with_complex_columns_resulting_into_long_names_partition as DBT_INTERNAL_DEST
      using nested_stream_with_complex_columns_resulting_into_long_names_partition__dbt_tmp as DBT_INTERNAL_SOURCE
      
      
    
        on false
    
  
      
      when matched then update set
         * 
    
      when not matched then insert *
