
      
    delete from "postgres".test_normalization."nested_stream_with_c__lting_into_long_names"
    where (_airbyte_unique_key) in (
        select (_airbyte_unique_key)
        from "nested_stream_with_c__lting_into_long_name__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."nested_stream_with_c__lting_into_long_names" ("_airbyte_unique_key", "id", "date", "partition", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_nested_stre__nto_long_names_hashid")
    (
        select "_airbyte_unique_key", "id", "date", "partition", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_nested_stre__nto_long_names_hashid"
        from "nested_stream_with_c__lting_into_long_name__dbt_tmp"
    )
  