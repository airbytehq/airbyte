
      
    delete from "postgres".test_normalization."nested_stream_with_c__lting_into_long_names_scd"
    where (_airbyte_unique_key_scd) in (
        select (_airbyte_unique_key_scd)
        from "nested_stream_with_c__lting_into_long_name__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."nested_stream_with_c__lting_into_long_names_scd" ("_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "date", "partition", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_nested_stre__nto_long_names_hashid")
    (
        select "_airbyte_unique_key", "_airbyte_unique_key_scd", "id", "date", "partition", "_airbyte_start_at", "_airbyte_end_at", "_airbyte_active_row", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_nested_stre__nto_long_names_hashid"
        from "nested_stream_with_c__lting_into_long_name__dbt_tmp"
    )
  