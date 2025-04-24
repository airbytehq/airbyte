
      
    delete from "postgres"._airbyte_test_normalization."nested_stream_with_c__lting_into_long_names_stg"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "nested_stream_with_c__lting_into_long_name__dbt_tmp"
    );
    

    insert into "postgres"._airbyte_test_normalization."nested_stream_with_c__lting_into_long_names_stg" ("_airbyte_nested_stre__nto_long_names_hashid", "id", "date", "partition", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at")
    (
        select "_airbyte_nested_stre__nto_long_names_hashid", "id", "date", "partition", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at"
        from "nested_stream_with_c__lting_into_long_name__dbt_tmp"
    )
  