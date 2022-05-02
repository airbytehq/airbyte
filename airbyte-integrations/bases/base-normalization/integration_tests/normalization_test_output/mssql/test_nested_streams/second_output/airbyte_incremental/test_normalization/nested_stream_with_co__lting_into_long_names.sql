
      
  
    delete from "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names"
    where (_airbyte_unique_key) in (
        select (_airbyte_unique_key)
        from "test_normalization".test_normalization."#nested_stream_with_co__lting_into_long_names__dbt_tmp"
    );
    

    insert into "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names" ("_airbyte_unique_key", "id", "date", "partition", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_nested_strea__nto_long_names_hashid")
    (
        select "_airbyte_unique_key", "id", "date", "partition", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_nested_strea__nto_long_names_hashid"
        from "test_normalization".test_normalization."#nested_stream_with_co__lting_into_long_names__dbt_tmp"
    );

  