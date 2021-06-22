

  create  table "postgres".test_normalization."dedup_cdc_excluded_scd__dbt_tmp"
  as (
    
        -- SQL model to build a Type 2 Slowly Changing Dimension (SCD) table for each record identified by their primary key
        select
            "id",
            val,
            "id" as _airbyte_start_at,
            lag("id") over (
                partition by "id"
                order by "id" desc, _airbyte_emitted_at desc
            ) as _airbyte_end_at,
            lag("id") over (
                partition by "id"
                order by "id" desc, _airbyte_emitted_at desc
            ) is null  as _airbyte_active_row,
            _airbyte_emitted_at,
            _airbyte_dedup_cdc_excluded_hashid
        from "postgres"._airbyte_test_normalization."dedup_cdc_excluded_ab4"
        -- dedup_cdc_excluded from "postgres".test_normalization._airbyte_raw_dedup_cdc_excluded
where _airbyte_row_num = 1
  );