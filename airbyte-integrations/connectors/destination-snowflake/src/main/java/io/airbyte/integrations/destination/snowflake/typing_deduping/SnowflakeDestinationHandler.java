/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.SQLException;
import java.util.LinkedHashMap;
import java.util.Optional;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeDestinationHandler implements DestinationHandler<SnowflakeTableDefinition> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeDestinationHandler.class);

  private final String databaseName;
  private final JdbcDatabase database;

  public SnowflakeDestinationHandler(String databaseName, JdbcDatabase database) {
    this.databaseName = databaseName;
    this.database = database;
  }

  @Override
  public Optional<SnowflakeTableDefinition> findExistingTable(StreamId id) throws SQLException {
    // The obvious database.getMetaData().getColumns() solution doesn't work, because JDBC translates
    // VARIANT as VARCHAR
    LinkedHashMap<String, String> columns = database.queryJsons(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_catalog = ?
          AND table_schema = ?
          AND table_name = ?
        ORDER BY ordinal_position;
        """,
        databaseName.toUpperCase(),
        id.finalNamespace(),
        id.finalName()).stream()
        .collect(LinkedHashMap::new,
            (map, row) -> map.put(row.get("COLUMN_NAME").asText(), row.get("DATA_TYPE").asText()),
            LinkedHashMap::putAll);
    // TODO query for indexes/partitioning/etc

    if (columns.isEmpty()) {
      return Optional.empty();
    } else {
      return Optional.of(new SnowflakeTableDefinition(columns));
    }
  }

  @Override
  public boolean isFinalTableEmpty(StreamId id) throws SQLException {
    int rowCount = database.queryInt(
        """
        SELECT row_count
        FROM information_schema.tables
        WHERE table_catalog = ?
          AND table_schema = ?
          AND table_name = ?
        """,
        databaseName,
        id.finalNamespace(),
        id.finalName());
    return rowCount == 0;
  }

  @Override
  public void execute(String sql) throws Exception {
    if ("".equals(sql)) {
      return;
    }
    final UUID queryId = UUID.randomUUID();
    LOGGER.info("Executing sql {}: {}", queryId, sql);
    long startTime = System.currentTimeMillis();

    database.execute(sql);

    LOGGER.info("Sql {} completed in {} ms", queryId, System.currentTimeMillis() - startTime);
  }

}
