
      
    delete from "postgres".test_normalization_namespace."simple_stream_with_n__lting_into_long_names"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "simple_stream_with_n__lting_into_long_name__dbt_tmp"
    );
    

    insert into "postgres".test_normalization_namespace."simple_stream_with_n__lting_into_long_names" ("id", "date", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_simple_stre__nto_long_names_hashid")
    (
        select "id", "date", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_simple_stre__nto_long_names_hashid"
        from "simple_stream_with_n__lting_into_long_name__dbt_tmp"
    )
  