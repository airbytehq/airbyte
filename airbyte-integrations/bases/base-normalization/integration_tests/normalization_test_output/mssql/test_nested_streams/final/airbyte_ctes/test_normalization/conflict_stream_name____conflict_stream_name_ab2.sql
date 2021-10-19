USE [test_normalization];
    execute('create view _airbyte_test_normalization."conflict_stream_name____conflict_stream_name_ab2__dbt_tmp" as
    
-- SQL model to cast each column to its adequate SQL type converted from the JSON schema type
select
    _airbyte_conflict_stream_name_2_hashid,
    cast(groups as 
    VARCHAR(max)) as groups,
    _airbyte_emitted_at
from "test_normalization"._airbyte_test_normalization."conflict_stream_name____conflict_stream_name_ab1"
-- conflict_stream_name at conflict_stream_name/conflict_stream_name/conflict_stream_name
    ');

