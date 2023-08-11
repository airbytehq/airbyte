package io.airbyte.integrations.source.mysql.initialsync;

import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifier;
import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import autovalue.shaded.com.google.common.collect.AbstractIterator;
import com.fasterxml.jackson.databind.JsonNode;
import com.mysql.cj.MysqlType;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.PrimaryKeyInfo;
import io.airbyte.integrations.source.mysql.internal.models.PrimaryKeyLoadStatus;
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

public class MySqlInitialLoadRecordIterator extends AbstractIterator<JsonNode>
    implements AutoCloseableIterator<JsonNode> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlInitialLoadRecordIterator.class);

  private final MySqlInitialLoadSourceOperations sourceOperations;

  private final String quoteString;
  private final MySqlInitialLoadStateManager initialLoadStateManager;
  private final List<String> columnNames;
  private final AirbyteStreamNameNamespacePair pair;
  private final JdbcDatabase database;
  // Represents the number of rows to get with each query.
  private final long chunkSize;
  private final PrimaryKeyInfo pkInfo;
  private int numSubqueries = 0;
  private AutoCloseableIterator<JsonNode> currentIterator;

  MySqlInitialLoadRecordIterator(
      final JdbcDatabase database,
      final MySqlInitialLoadSourceOperations sourceOperations,
      final String quoteString,
      final MySqlInitialLoadStateManager initialLoadStateManager,
      final List<String> columnNames,
      final AirbyteStreamNameNamespacePair pair,
      final long chunkSize) {
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.initialLoadStateManager = initialLoadStateManager;
    this.columnNames = columnNames;
    this.pair = pair;
    this.chunkSize = chunkSize;
    this.pkInfo = initialLoadStateManager.getPrimaryKeyInfo(pair);
  }

  @CheckForNull
  @Override
  protected JsonNode computeNext() {
    if (currentIterator == null || !currentIterator.hasNext()) {
      try {
        LOGGER.info("Subquery number : {}", numSubqueries);
        final Stream<JsonNode> stream = database.unsafeQuery(
            connection -> getPkPreparedStatement(connection), sourceOperations::rowToJson);

        // Previous stream (and connection) must be manually closed in this iterator.
        if (currentIterator != null) {
          currentIterator.close();
        }
        currentIterator = AutoCloseableIterators.fromStream(stream, pair);
        numSubqueries++;
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }
    if (!currentIterator.hasNext()) {
      return endOfData();
    }
    return currentIterator.next();
  }

  private PreparedStatement getPkPreparedStatement(final Connection connection) {
    try {
      final String tableName = pair.getName();
      final String schemaName = pair.getNamespace();
      LOGGER.info("Preparing query for table: {}", tableName);
      final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, tableName,
          quoteString);

      final String wrappedColumnNames = RelationalDbQueryUtils.enquoteIdentifierList(columnNames, quoteString);

      final PrimaryKeyLoadStatus pkLoadStatus = initialLoadStateManager.getPrimaryKeyLoadStatus(pair);

      if (pkLoadStatus == null) {
        LOGGER.info("pkLoadStatus is null");
        final String quotedCursorField = enquoteIdentifier(pkInfo.pkFieldName(), quoteString);
        final String sql = String.format("SELECT %s FROM %s ORDER BY %s LIMIT %s", wrappedColumnNames, fullTableName,
            quotedCursorField, chunkSize);
        final PreparedStatement preparedStatement = connection.prepareStatement(sql);
        return preparedStatement;

      } else {
        LOGGER.info("pkLoadStatus value is : {}", pkLoadStatus.getPkVal());
        final String quotedCursorField = enquoteIdentifier(pkLoadStatus.getPkName(), quoteString);
        // Since a pk is unique, we can issue a > query instead of a >=, as there cannot be two records with the same pk.
        final String sql = String.format("SELECT %s FROM %s WHERE %s > ? ORDER BY %s LIMIT %s", wrappedColumnNames, fullTableName,
            quotedCursorField, quotedCursorField, chunkSize);
        final PreparedStatement preparedStatement = connection.prepareStatement(sql);
        final MysqlType cursorFieldType = pkInfo.fieldType();
        sourceOperations.setCursorField(preparedStatement, 1, cursorFieldType, pkLoadStatus.getPkVal());

        LOGGER.info("Executing query for table {}: {}", tableName, preparedStatement);
        return preparedStatement;
      }
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public void close() throws Exception {
    if (currentIterator != null) {
      currentIterator.close();
    }
  }
}
