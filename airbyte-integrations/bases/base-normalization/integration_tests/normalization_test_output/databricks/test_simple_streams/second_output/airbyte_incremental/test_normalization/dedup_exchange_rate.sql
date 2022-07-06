
    
  
  
    merge into test_normalization.`dedup_exchange_rate` as DBT_INTERNAL_DEST
      using `dedup_exchange_rate__dbt_tmp` as DBT_INTERNAL_SOURCE
      
      
    
        on DBT_INTERNAL_SOURCE._airbyte_unique_key = DBT_INTERNAL_DEST._airbyte_unique_key
    
  
      
      when matched then update set
         * 
    
      when not matched then insert *
