
      
  
    delete from "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names_scd"
    where (_airbyte_unique_key_scd) in (
        select (_airbyte_unique_key_scd)
        from "test_normalization".test_normalization."#nested_stream_with_co__lting_into_long_names_scd__dbt_tmp"
    );
    

    insert into "test_normalization".test_normalization."nested_stream_with_co__lting_into_long_names_scd" ("_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "date", "partition", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_nested_strea__nto_long_names_hashid")
    (
        select "_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "date", "partition", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_nested_strea__nto_long_names_hashid"
        from "test_normalization".test_normalization."#nested_stream_with_co__lting_into_long_names_scd__dbt_tmp"
    );

  