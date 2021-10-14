USE [test_normalization];
    execute('create view _airbyte_test_normalization."dedup_cdc_excluded_ab2__dbt_tmp" as
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    cast(id as 
    bigint
) as id,
    cast(name as 
    VARCHAR(max)) as name,
    cast("column`_''with""_quotes" as 
    VARCHAR(max)) as "column`_''with""_quotes",
    cast(_ab_cdc_lsn as 
    float
) as _ab_cdc_lsn,
    cast(_ab_cdc_updated_at as 
    float
) as _ab_cdc_updated_at,
    cast(_ab_cdc_deleted_at as 
    float
) as _ab_cdc_deleted_at,
    _airbyte_emitted_at
from "test_normalization"._airbyte_test_normalization."dedup_cdc_excluded_ab1"
-- dedup_cdc_excluded
    ');

