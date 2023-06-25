package io.airbyte.integrations.source.postgres.standard;

import io.airbyte.db.JdbcCompatibleSourceOperations;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.postgres.internal.models.StandardStatus;
import io.airbyte.integrations.source.postgres.xmin.PostgresXminHandler;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresStandardHandler {
  private final JdbcCompatibleSourceOperations sourceOperations;
  private final JdbcDatabase database;
  private final String quoteString;
  private final StandardStatus currentSyncStatus;
  private final StateManager stateManager;
  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresXminHandler.class);

  public PostgresStandardHandler(final JdbcDatabase database,
                                 final JdbcCompatibleSourceOperations sourceOperations,
                                 final String quoteString,
                                 final StandardStatus currentSyncStatus,
                                 final StateManager stateManager) {
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.currentSyncStatus = currentSyncStatus;
    this.stateManager = stateManager;
  }
}
