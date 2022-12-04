
      
    delete from "postgres".test_normalization."1_prefix_startwith_number"
    where (_airbyte_unique_key) in (
        select (_airbyte_unique_key)
        from "1_prefix_startwith_number__dbt_tmp"
    );
    

    insert into "postgres".test_normalization."1_prefix_startwith_number" ("_airbyte_unique_key", "id", "date", "text", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_1_prefix_startwith_number_hashid")
    (
        select "_airbyte_unique_key", "id", "date", "text", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_1_prefix_startwith_number_hashid"
        from "1_prefix_startwith_number__dbt_tmp"
    )
  