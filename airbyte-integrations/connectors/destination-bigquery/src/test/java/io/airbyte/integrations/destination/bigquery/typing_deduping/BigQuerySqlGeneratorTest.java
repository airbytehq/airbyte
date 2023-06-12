package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.cloud.bigquery.StandardSQLTypeName;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.StreamConfig;
import io.airbyte.integrations.destination.bigquery.typing_deduping.SqlGenerator.QuotedColumnId;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class BigQuerySqlGeneratorTest {

  private final BigQuerySqlGenerator generator = new BigQuerySqlGenerator();

  @Test
  public void basicCreateTable() {
    LinkedHashMap<QuotedColumnId, StandardSQLTypeName> columns = new LinkedHashMap<>();
    columns.put(generator.quoteColumnId("id"), StandardSQLTypeName.INT64);
    columns.put(generator.quoteColumnId("updated_at"), StandardSQLTypeName.TIMESTAMP);
    columns.put(generator.quoteColumnId("name"), StandardSQLTypeName.STRING);
    StreamConfig<StandardSQLTypeName> stream = new StreamConfig<>(
        new SqlGenerator.QuotedStreamId("public", "users", "airbyte", "public_users", "public", "users"),
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        List.of(generator.quoteColumnId("id")),
        Optional.of(generator.quoteColumnId("updated_at")),
        columns
    );

    final String sql = generator.createTable(stream);

    assertEquals(
        """
            CREATE TABLE public.users (
            _airbyte_raw_id STRING NOT NULL,
            _airbyte_extracted_at TIMESTAMP NOT NULL,
            _airbyte_meta JSON NOT NULL,
            id INT64,
            updated_at TIMESTAMP,
            name STRING
            )
            PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
            CLUSTER BY id, _airbyte_extracted_at
            """,
        sql
    );
  }

  @Test
  public void basicIncrementalDedupUpdateTable() {
    LinkedHashMap<QuotedColumnId, StandardSQLTypeName> columns = new LinkedHashMap<>();
    columns.put(generator.quoteColumnId("id"), StandardSQLTypeName.INT64);
    columns.put(generator.quoteColumnId("updated_at"), StandardSQLTypeName.TIMESTAMP);
    columns.put(generator.quoteColumnId("name"), StandardSQLTypeName.STRING);
    StreamConfig<StandardSQLTypeName> stream = new StreamConfig<>(
        new SqlGenerator.QuotedStreamId("public", "users", "airbyte", "public_users", "public", "users"),
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        List.of(generator.quoteColumnId("id")),
        Optional.of(generator.quoteColumnId("updated_at")),
        columns
    );

    final String sql = generator.updateTable("", stream);

    assertEquals(
        """
            BEGIN TRANSACTION;
            DECLARE missing_pk_count INT64;

            SET missing_pk_count = (
              SELECT COUNT(1)
              FROM airbyte.public_users
              WHERE
                `_airbyte_loaded_at` IS NULL
                AND SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$.id') as INT64) IS NULL
              );
                        
            IF missing_pk_count > 0 THEN
              RAISE USING message = FORMAT("Raw table has %s rows missing a primary key", CAST(missing_pk_count AS STRING));
            END IF;
                        
              INSERT INTO public.users
              SELECT
            SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$.id') as INT64) as id,
            SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$.updated_at') as TIMESTAMP) as updated_at,
            SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$.name') as STRING) as name,
            to_json(struct(array_concat(
            CASE
              WHEN (JSON_VALUE(`_airbyte_data`, '$.id') IS NOT NULL) AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$.id') as INT64) IS NULL) THEN ["Problem with `id`"]
              ELSE []
            END,
            CASE
              WHEN (JSON_VALUE(`_airbyte_data`, '$.updated_at') IS NOT NULL) AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$.updated_at') as TIMESTAMP) IS NULL) THEN ["Problem with `updated_at`"]
              ELSE []
            END,
            CASE
              WHEN (JSON_VALUE(`_airbyte_data`, '$.name') IS NOT NULL) AND (SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$.name') as STRING) IS NULL) THEN ["Problem with `name`"]
              ELSE []
            END
            ) as errors)) as _airbyte_meta,
                _airbyte_raw_id,
                _airbyte_extracted_at
              FROM airbyte.public_users
              WHERE
                _airbyte_loaded_at IS NULL
                AND JSON_EXTRACT(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NULL
              ;
                      
              DELETE FROM public.users
              WHERE
                `_airbyte_raw_id` IN (
                  SELECT `_airbyte_raw_id` FROM (
                    SELECT `_airbyte_raw_id`, row_number() OVER (
                      PARTITION BY id ORDER BY `updated_at` DESC, `_airbyte_extracted_at` DESC
                    ) as row_number FROM public.users
                  )
                  WHERE row_number != 1
                )
                OR (
            `id` IN (
              SELECT
                SAFE_CAST(JSON_VALUE(`_airbyte_data`, '$.id') as INT64) as id
              FROM airbyte.public_users
              WHERE JSON_VALUE(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NOT NULL
            )
                )
              ;
                      
            DELETE FROM
              airbyte.public_users
            WHERE
              `_airbyte_raw_id` NOT IN (
                SELECT `_airbyte_raw_id` FROM public.users
              )
              AND
              JSON_VALUE(`_airbyte_data`, '$._ab_cdc_deleted_at') IS NULL
            ;
                      
            UPDATE airbyte.public_users
            SET `_airbyte_loaded_at` = CURRENT_TIMESTAMP()
            WHERE `_airbyte_loaded_at` IS NULL
            ;
                      
            COMMIT TRANSACTION;
            """,
        sql
    );
  }
}
