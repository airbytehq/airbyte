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

/**
 * This record iterator operates over a single stream. It continuously reads data from a table via multiple queries with the configured
 * chunk size until the entire table is processed. The next query uses the highest watermark of the primary key seen in the previous
 * subquery. Consider a table with chunk size = 1,000,000, and 3,500,000 records. The series of queries executed are :
 * Query 1 : select * from table order by pk limit 1,800,000, pk_max = pk_max_1
 * Query 2 : select * from table where pk > pk_max_1 order by pk limit 1,800,000, pk_max = pk_max_2
 * Query 3 : select * from table where pk > pk_max_2 order by pk limit 1,800,000, pk_max = pk_max_3
 * Query 4 : select * from table where pk > pk_max_3 order by pk limit 1,800,000, pk_max = pk_max_4
 * Query 5 : select * from table where pk > pk_max_4 order by pk limit 1,800,000. Final query, since there are zero records processed here.
 */
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
    if (shouldBuildNextSubquery()) {
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
        // If the current subquery has no records associated with it, the entire stream has been read.
        if (!currentIterator.hasNext()) {
          return endOfData();
        }
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }
    return currentIterator.next();
  }

  private boolean shouldBuildNextSubquery() {
    // The next sub-query should be built if (i) it is the first subquery in the sequence. (ii) the previous subquery has finished.
    return currentIterator == null || !currentIterator.hasNext();
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
        LOGGER.info("Executing query for table {}: {}", tableName, preparedStatement);
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
