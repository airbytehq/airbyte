package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static org.junit.jupiter.api.Assertions.*;

import com.google.cloud.bigquery.StandardSQLTypeName;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.StreamConfig;
import io.airbyte.integrations.destination.bigquery.typing_deduping.SqlGenerator.QuotedColumnId;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.stream.Collectors;
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
}
