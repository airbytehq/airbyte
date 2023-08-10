package io.airbyte.integrations.source.mysql.initialsync;

import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import autovalue.shaded.com.google.common.collect.AbstractIterator;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadHandler.SubQueryPlan;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.PrimaryKeyInfo;
import io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Stream;
import javax.annotation.CheckForNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlInitialLoadRecordIterator<JsonNode> extends AbstractIterator<JsonNode>
    implements AutoCloseableIterator<JsonNode> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlInitialLoadRecordIterator.class);

  private final MySqlInitialLoadSourceOperations sourceOperations;

  private final String quoteString;
  private final MySqlInitialLoadStateManager initialLoadStateManager;
  private final List<String> columnNames;
  private final AirbyteStreamNameNamespacePair pair;
  private final JdbcDatabase database;

  MySqlInitialLoadRecordIterator(
      final JdbcDatabase database,
      final MySqlInitialLoadSourceOperations sourceOperations,
      final String quoteString,
      final MySqlInitialLoadStateManager initialLoadStateManager,
      final List<String> columnNames,
      final String schemaName,
      final String tableName) {
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.initialLoadStateManager = initialLoadStateManager;
    this.columnNames = columnNames;
    this.pair = AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);
  }

  @CheckForNull
  @Override
  protected JsonNode computeNext() {
    final Stream<JsonNode> stream = database.unsafeQuery(
        connection -> createPkQueryStatement(connection, columnNames, schemaName, tableName, pair, pkInfo,
            subQueriesPlan, isFinalSubquery), sourceOperations::rowToJson);
    return;
  }

  private PreparedStatement createPkQueryStatement(
      final Connection connection,
      final List<String> columnNames,
      final String schemaName,
      final String tableName,
      final AirbyteStreamNameNamespacePair airbyteStream,
      final PrimaryKeyInfo pkInfo,
      final SubQueryPlan subQueryPlan,
      final boolean isFinalSubquery) {
    try {
      LOGGER.info("Preparing query for table: {}", tableName);
      final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, tableName,
          quoteString);

      final String wrappedColumnNames = RelationalDbQueryUtils.enquoteIdentifierList(columnNames, quoteString);

      final PreparedStatement preparedStatement =
          getPkPreparedStatement(connection, wrappedColumnNames, fullTableName, airbyteStream, pkInfo, subQueryPlan, isFinalSubquery);
      LOGGER.info("Executing query for table {}: {}", tableName, preparedStatement);
      return preparedStatement;
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }
  @Override
  public void close() throws Exception {

  }
}
