package io.airbyte.integrations.destination.snowflake.typing_deduping;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import net.snowflake.client.jdbc.SnowflakeType;
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
    // TODO these names are case-sensitive, make a decision about this https://github.com/airbytehq/airbyte/issues/28638
    List<SnowflakeColumn> columns = database.queryJsons(String.format(
        """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_catalog = '%s'
              AND table_schema = '%s'
              AND table_name = '%s'
            ORDER BY ordinal_position;
            """,
        databaseName,
        id.finalNamespace(),
        id.finalName()
        )).stream()
        .map(column -> new SnowflakeColumn(
            column.get("COLUMN_NAME").asText(),
            SnowflakeType.valueOf(column.get("DATA_TYPE").asText())))
        .toList();
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
