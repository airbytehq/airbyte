
      
    delete from "postgres"._airbyte_test_normalization."1_prefix_startwith_number_stg"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "1_prefix_startwith_number_stg__dbt_tmp"
    );
    

    insert into "postgres"._airbyte_test_normalization."1_prefix_startwith_number_stg" ("_airbyte_1_prefix_startwith_number_hashid", "id", "date", "text", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at")
    (
        select "_airbyte_1_prefix_startwith_number_hashid", "id", "date", "text", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at"
        from "1_prefix_startwith_number_stg__dbt_tmp"
    )
  