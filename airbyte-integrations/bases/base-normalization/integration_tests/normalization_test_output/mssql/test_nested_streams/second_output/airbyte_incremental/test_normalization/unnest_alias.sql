
      delete
    from "test_normalization".test_normalization."unnest_alias"
    where (_airbyte_ab_id) in (
        select (_airbyte_ab_id)
        from "test_normalization".test_normalization."#unnest_alias__dbt_tmp"
    );

    insert into "test_normalization".test_normalization."unnest_alias" ("id", "children", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_unnest_alias_hashid")
    (
       select "id", "children", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_normalized_at", "_airbyte_unnest_alias_hashid"
       from "test_normalization".test_normalization."#unnest_alias__dbt_tmp"
    );
  