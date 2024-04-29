BEGIN;
insert into "test_schema"."users_finalunittest" (
    "id1",
    "id2",
    "updated_at",
    "struct",
    "array",
    "string",
    "number",
    "integer",
    "boolean",
    "timestamp_with_timezone",
    "timestamp_without_timezone",
    "time_with_timezone",
    "time_without_timezone",
    "date",
    "unknown",
    "_ab_cdc_deleted_at",
    "_airbyte_raw_id",
    "_airbyte_extracted_at",
    "_airbyte_meta"
)
with
    "intermediate_data" as (
        select
            cast("_airbyte_data"."id1" as bigint) as "id1",
            cast("_airbyte_data"."id2" as bigint) as "id2",
            cast("_airbyte_data"."updated_at" as timestamp with time zone) as "updated_at",
            CASE WHEN JSON_TYPEOF("_airbyte_data"."struct") = 'object' THEN cast("_airbyte_data"."struct" as super) END  as "struct",
            CASE WHEN JSON_TYPEOF("_airbyte_data"."array") = 'array' THEN cast("_airbyte_data"."array" as super) END  as "array",
            CASE WHEN (
                JSON_TYPEOF("_airbyte_data"."string") <> 'string'
                    and "_airbyte_data"."string" is not null
                ) THEN JSON_SERIALIZE("_airbyte_data"."string") ELSE cast("_airbyte_data"."string" as varchar(65535)) END  as "string",
            cast("_airbyte_data"."number" as decimal(38, 9)) as "number",
            cast("_airbyte_data"."integer" as bigint) as "integer",
            cast("_airbyte_data"."boolean" as boolean) as "boolean",
            cast("_airbyte_data"."timestamp_with_timezone" as timestamp with time zone) as "timestamp_with_timezone",
            cast("_airbyte_data"."timestamp_without_timezone" as timestamp) as "timestamp_without_timezone",
            cast("_airbyte_data"."time_with_timezone" as time with time zone) as "time_with_timezone",
            cast("_airbyte_data"."time_without_timezone" as time) as "time_without_timezone",
            cast("_airbyte_data"."date" as date) as "date",
            cast("_airbyte_data"."unknown" as super) as "unknown",
            cast("_airbyte_data"."_ab_cdc_deleted_at" as timestamp with time zone) as "_ab_cdc_deleted_at",
            "_airbyte_raw_id",
            "_airbyte_extracted_at",
            OBJECT(
                'changes',
                    ARRAY_CONCAT(
                            ARRAY_CONCAT(
                                    ARRAY_CONCAT(
                                            ARRAY_CONCAT(
                                                    ARRAY_CONCAT(
                                                            ARRAY_CONCAT(
                                                                    ARRAY_CONCAT(
                                                                            ARRAY_CONCAT(
                                                                                    ARRAY_CONCAT(
                                                                                            ARRAY_CONCAT(
                                                                                                    ARRAY_CONCAT(
                                                                                                            ARRAY_CONCAT(
                                                                                                                    ARRAY_CONCAT(
                                                                                                                            ARRAY_CONCAT(
                                                                                                                                    ARRAY_CONCAT(
                                                                                                                                            ARRAY_CONCAT(
                                                                                                                                                    CASE WHEN (
                                                                                                                                                            "_airbyte_data"."id1" is not null
                                                                                                                                                                and "id1" is null
                                                                                                                                                            ) THEN ARRAY(JSON_PARSE('{"field": "id1", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END ,
                                                                                                                                                    CASE WHEN (
                                                                                                                                                            "_airbyte_data"."id2" is not null
                                                                                                                                                                and "id2" is null
                                                                                                                                                            ) THEN ARRAY(JSON_PARSE('{"field": "id2", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                                                                                                                            ),
                                                                                                                                            CASE WHEN (
                                                                                                                                                    "_airbyte_data"."updated_at" is not null
                                                                                                                                                        and "updated_at" is null
                                                                                                                                                    ) THEN ARRAY(JSON_PARSE('{"field": "updated_at", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                                                                                                                    ),
                                                                                                                                    CASE WHEN (
                                                                                                                                            "_airbyte_data"."struct" is not null
                                                                                                                                                and "struct" is null
                                                                                                                                            ) THEN ARRAY(JSON_PARSE('{"field": "struct", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                                                                                                            ),
                                                                                                                            CASE WHEN (
                                                                                                                                    "_airbyte_data"."array" is not null
                                                                                                                                        and "array" is null
                                                                                                                                    ) THEN ARRAY(JSON_PARSE('{"field": "array", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                                                                                                    ),
                                                                                                                    CASE WHEN (
                                                                                                                            "_airbyte_data"."string" is not null
                                                                                                                                and "string" is null
                                                                                                                            ) THEN ARRAY(JSON_PARSE('{"field": "string", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                                                                                            ),
                                                                                                            CASE WHEN (
                                                                                                                    "_airbyte_data"."number" is not null
                                                                                                                        and "number" is null
                                                                                                                    ) THEN ARRAY(JSON_PARSE('{"field": "number", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                                                                                    ),
                                                                                                    CASE WHEN (
                                                                                                            "_airbyte_data"."integer" is not null
                                                                                                                and "integer" is null
                                                                                                            ) THEN ARRAY(JSON_PARSE('{"field": "integer", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                                                                            ),
                                                                                            CASE WHEN (
                                                                                                    "_airbyte_data"."boolean" is not null
                                                                                                        and "boolean" is null
                                                                                                    ) THEN ARRAY(JSON_PARSE('{"field": "boolean", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                                                                    ),
                                                                                    CASE WHEN (
                                                                                            "_airbyte_data"."timestamp_with_timezone" is not null
                                                                                                and "timestamp_with_timezone" is null
                                                                                            ) THEN ARRAY(JSON_PARSE('{"field": "timestamp_with_timezone", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                                                            ),
                                                                            CASE WHEN (
                                                                                    "_airbyte_data"."timestamp_without_timezone" is not null
                                                                                        and "timestamp_without_timezone" is null
                                                                                    ) THEN ARRAY(JSON_PARSE('{"field": "timestamp_without_timezone", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                                                    ),
                                                                    CASE WHEN (
                                                                            "_airbyte_data"."time_with_timezone" is not null
                                                                                and "time_with_timezone" is null
                                                                            ) THEN ARRAY(JSON_PARSE('{"field": "time_with_timezone", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                                            ),
                                                            CASE WHEN (
                                                                    "_airbyte_data"."time_without_timezone" is not null
                                                                        and "time_without_timezone" is null
                                                                    ) THEN ARRAY(JSON_PARSE('{"field": "time_without_timezone", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                                    ),
                                                    CASE WHEN (
                                                            "_airbyte_data"."date" is not null
                                                                and "date" is null
                                                            ) THEN ARRAY(JSON_PARSE('{"field": "date", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                            ),
                                            CASE WHEN (
                                                    "_airbyte_data"."unknown" is not null
                                                        and "unknown" is null
                                                    ) THEN ARRAY(JSON_PARSE('{"field": "unknown", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                                    ),
                                    CASE WHEN (
                                            "_airbyte_data"."_ab_cdc_deleted_at" is not null
                                                and "_ab_cdc_deleted_at" is null
                                            ) THEN ARRAY(JSON_PARSE('{"field": "_ab_cdc_deleted_at", "change": "NULLED", "reason": "DESTINATION_TYPECAST_ERROR"}')) ELSE ARRAY() END
                            ),
                            CASE WHEN (
                                "_airbyte_meta" is not null
                                    and IS_OBJECT("_airbyte_meta")
                                    and "_airbyte_meta"."changes" is not null
                                    and IS_ARRAY("_airbyte_meta"."changes")
                                ) THEN "_airbyte_meta"."changes" ELSE ARRAY() END
                    )
            ) as "_airbyte_meta"
        from "test_schema"."users_raw"
        where (
                  (
                      "_airbyte_loaded_at" is null
                          or (
                          "_airbyte_loaded_at" is not null
                              and JSON_TYPEOF("_airbyte_data"."_ab_cdc_deleted_at") <> 'null'
                          )
                      )
                      and "_airbyte_extracted_at" > '2023-02-15T18:35:24Z'
                  )
    ),
    "numbered_rows" as (
        select
            *,
            row_number() over (
                partition by "id1", "id2"
            order by
                "updated_at" desc NULLS LAST,
                "_airbyte_extracted_at" desc
            ) as "row_number"
        from "intermediate_data"
    )
select
    "id1",
    "id2",
    "updated_at",
    "struct",
    "array",
    "string",
    "number",
    "integer",
    "boolean",
    "timestamp_with_timezone",
    "timestamp_without_timezone",
    "time_with_timezone",
    "time_without_timezone",
    "date",
    "unknown",
    "_ab_cdc_deleted_at",
    "_airbyte_raw_id",
    "_airbyte_extracted_at",
    "_airbyte_meta"
from "numbered_rows"
where "row_number" = 1;
delete from "test_schema"."users_finalunittest"
where "_airbyte_raw_id" in (
    select "_airbyte_raw_id"
    from (
             select
                 "_airbyte_raw_id",
                 row_number() over (
                    partition by "id1", "id2"
                order by
                    "updated_at" desc NULLS LAST,
                    "_airbyte_extracted_at" desc
                ) as "row_number"
             from "test_schema"."users_finalunittest"
         ) as "airbyte_ids"
    where "row_number" <> 1
);
delete from "test_schema"."users_finalunittest"
where "_ab_cdc_deleted_at" is not null;
update "test_schema"."users_raw"
set
"_airbyte_loaded_at" = GETDATE()
where (
          "_airbyte_loaded_at" is null
              and "_airbyte_extracted_at" > '2023-02-15T18:35:24Z'
          );
COMMIT;
