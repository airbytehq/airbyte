/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

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
 * This record iterator operates over a single stream. It continuously reads data from a table via
 * multiple queries with the configured chunk size until the entire table is processed. The next
 * query uses the highest watermark of the primary key seen in the previous subquery. Consider a
 * table with chunk size = 1,000,000, and 3,500,000 records. The series of queries executed are :
 * Query 1 : select * from table order by pk limit 1,800,000, pk_max = pk_max_1 Query 2 : select *
 * from table where pk > pk_max_1 order by pk limit 1,800,000, pk_max = pk_max_2 Query 3 : select *
 * from table where pk > pk_max_2 order by pk limit 1,800,000, pk_max = pk_max_3 Query 4 : select *
 * from table where pk > pk_max_3 order by pk limit 1,800,000, pk_max = pk_max_4 Query 5 : select *
 * from table where pk > pk_max_4 order by pk limit 1,800,000. Final query, since there are zero
 * records processed here.
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
  private final boolean isCompositeKeyLoad;
  private int numSubqueries = 0;
  private AutoCloseableIterator<JsonNode> currentIterator;

  MySqlInitialLoadRecordIterator(
                                 final JdbcDatabase database,
                                 final MySqlInitialLoadSourceOperations sourceOperations,
                                 final String quoteString,
                                 final MySqlInitialLoadStateManager initialLoadStateManager,
                                 final List<String> columnNames,
                                 final AirbyteStreamNameNamespacePair pair,
                                 final long chunkSize,
                                 final boolean isCompositeKeyLoad) {
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.initialLoadStateManager = initialLoadStateManager;
    this.columnNames = columnNames;
    this.pair = pair;
    this.chunkSize = chunkSize;
    this.pkInfo = initialLoadStateManager.getPrimaryKeyInfo(pair);
    this.isCompositeKeyLoad = isCompositeKeyLoad;
  }

  @CheckForNull
  @Override
  protected JsonNode computeNext() {
    if (shouldBuildNextSubquery()) {
      try {
        // We will only issue one query for a composite key load. If we have already processed all the data
        // associated with this
        // query, we should indicate that we are done processing for the given stream.
        if (isCompositeKeyLoad && numSubqueries >= 1) {
          return endOfData();
        }
        // Previous stream (and connection) must be manually closed in this iterator.
        if (currentIterator != null) {
          currentIterator.close();
        }

        LOGGER.info("Subquery number : {}", numSubqueries);
        final Stream<JsonNode> stream = database.unsafeQuery(
            this::getPkPreparedStatement, sourceOperations::rowToJson);

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
    // The next sub-query should be built if (i) it is the first subquery in the sequence. (ii) the
    // previous subquery has finished.
    return (currentIterator == null || !currentIterator.hasNext());
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
        final String sql;
        // We cannot load in chunks for a composite key load, since each field might not have distinct
        // values.
        if (isCompositeKeyLoad) {
          sql = String.format("SELECT %s FROM %s ORDER BY %s", wrappedColumnNames, fullTableName,
              quotedCursorField);
        } else {
          sql = String.format("SELECT %s FROM %s ORDER BY %s LIMIT %s", wrappedColumnNames, fullTableName,
              quotedCursorField, chunkSize);
        }
        final PreparedStatement preparedStatement = connection.prepareStatement(sql);
        LOGGER.info("Executing query for table {}: {}", tableName, preparedStatement);
        return preparedStatement;
      } else {
        LOGGER.info("pkLoadStatus value is : {}", pkLoadStatus.getPkVal());
        final String quotedCursorField = enquoteIdentifier(pkLoadStatus.getPkName(), quoteString);
        final String sql;
        // We cannot load in chunks for a composite key load, since each field might not have distinct
        // values. Furthermore, we have to issue a >=
        // query since we may not have processed all of the data associated with the last saved primary key
        // value.
        if (isCompositeKeyLoad) {
          sql = String.format("SELECT %s FROM %s WHERE %s >= ? ORDER BY %s", wrappedColumnNames, fullTableName,
              quotedCursorField, quotedCursorField);
        } else {
          // The pk max value could be null - this can happen in the case of empty tables. In this case, we
          // can just issue a query
          // without any chunking.
          if (pkInfo.pkMaxValue() != null) {
            sql = String.format("SELECT %s FROM %s WHERE %s > ? AND %s <= ? ORDER BY %s LIMIT %s", wrappedColumnNames, fullTableName,
                quotedCursorField, quotedCursorField, quotedCursorField, chunkSize);
          } else {
            sql = String.format("SELECT %s FROM %s WHERE %s > ? ORDER BY %s", wrappedColumnNames, fullTableName,
                quotedCursorField, quotedCursorField);
          }
        }
        final PreparedStatement preparedStatement = connection.prepareStatement(sql);
        final MysqlType cursorFieldType = pkInfo.fieldType();
        sourceOperations.setCursorField(preparedStatement, 1, cursorFieldType, pkLoadStatus.getPkVal());
        if (!isCompositeKeyLoad && pkInfo.pkMaxValue() != null) {
          sourceOperations.setCursorField(preparedStatement, 2, cursorFieldType, pkInfo.pkMaxValue());
        }
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
