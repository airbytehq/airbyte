package io.airbyte.integrations.source.postgres;

import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.time.Instant;
import java.util.Map;
import javax.annotation.CheckForNull;

public class XminRecordIterator<T> extends AbstractIterator<AirbyteMessage>
    implements AutoCloseableIterator<AirbyteMessage> {

  private final JdbcDatabase database;
  private final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable;
  private final StateManager stateManager;
  private final Instant emittedAt;


  public XminRecordIterator(final JdbcDatabase database,
      final ConfiguredAirbyteCatalog catalog,
      final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
      final StateManager stateManager,
      final Instant emittedAt) {
    this.database = database;
    this.tableNameToTable = tableNameToTable;
    this.stateManager = stateManager;
    this.emittedAt = emittedAt;
  }

  @CheckForNull
  @Override
  protected AirbyteMessage computeNext() {
    //database.
    return null;
  }

  @Override
  public void close() throws Exception {

  }
}
