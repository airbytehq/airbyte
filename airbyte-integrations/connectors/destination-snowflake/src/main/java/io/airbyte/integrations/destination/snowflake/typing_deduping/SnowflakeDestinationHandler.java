package io.airbyte.integrations.destination.snowflake.typing_deduping;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.SQLException;
import java.util.Optional;

public class SnowflakeDestinationHandler implements DestinationHandler<SnowflakeTableDefinition> {

  private final JdbcDatabase database;

  public SnowflakeDestinationHandler(JdbcDatabase database) {
    this.database = database;
  }

  @Override
  public Optional<SnowflakeTableDefinition> findExistingTable(StreamId id) throws SQLException {
    // TODO only fetch metadata once
    database.getMetaData();
    return Optional.empty();
  }

  @Override
  public boolean isFinalTableEmpty(StreamId id) {
    return false;
  }

  @Override
  public void execute(String sql) throws Exception {

  }
}
