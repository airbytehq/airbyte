
  create view "postgres"._airbyte_test_normalization."dedup_cdc_excluded_ab2__dbt_tmp" as (
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast("id" as 
    bigint
) as "id",
    cast(val as 
    varchar
) as val,
    _airbyte_emitted_at
from "postgres"._airbyte_test_normalization."dedup_cdc_excluded_ab1"
-- dedup_cdc_excluded
  );
