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
    StreamConfig<StandardSQLTypeName> stream = new StreamConfig<>(
        new SqlGenerator.QuotedStreamId("public", "users", "airbyte", "public_users", "public", "users"),
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        List.of(generator.quoteColumnId("id")),
        Optional.of(generator.quoteColumnId("updated_at")),
        Map.of(
            generator.quoteColumnId("id"), StandardSQLTypeName.INT64,
            generator.quoteColumnId("updated_at"), StandardSQLTypeName.TIMESTAMP,
            generator.quoteColumnId("name"), StandardSQLTypeName.STRING
        ).entrySet().stream().collect(Collectors.toMap(
            Entry::getKey,
            Entry::getValue,
            (a, b) -> a,
            LinkedHashMap::new
        ))
    );

    final String sql = generator.createTable(stream);

    assertEquals(
        """
            CREATE TABLE public.users (
            _airbyte_raw_id STRING,
            _airbyte_extracted_at TIMESTAMP,
            _airbyte_meta JSON,
            id INT64,
            updated_at TIMESTAMP,
            name STRING
            )
            """,
        sql
    );
  }
}
