/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import static io.airbyte.cdk.db.DbAnalyticsUtils.cdcSnapshotForceShutdownMessage;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;
import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIteratorConstants.EIGHT_KB;
import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIteratorConstants.GIGABYTE;
import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIteratorConstants.MAX_ALLOWED_RESYNCS;
import static io.airbyte.integrations.source.postgres.ctid.InitialSyncCtidIteratorConstants.QUERY_TARGET_SIZE_GB;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.collect.AbstractIterator;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils;
import io.airbyte.commons.exceptions.TransientErrorException;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils;
import io.airbyte.integrations.source.postgres.ctid.CtidPostgresSourceOperations.RowDataWithCtid;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Optional;
import java.util.Queue;
import java.util.stream.Stream;
import javax.annotation.CheckForNull;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is responsible to divide the data of the stream into chunks based on the ctid and
 * dynamically create iterator and keep processing them one after another. The class also makes sure
 * to check for VACUUM in between processing chunks and if VACUUM happens then re-start syncing the
 * data
 */
public class InitialSyncCtidIterator extends AbstractIterator<RowDataWithCtid> implements AutoCloseableIterator<RowDataWithCtid> {

  private static final Logger LOGGER = LoggerFactory.getLogger(InitialSyncCtidIterator.class);
  public static final int MAX_TUPLES_IN_QUERY = 5_000_000;
  private final AirbyteStreamNameNamespacePair airbyteStream;
  private final long blockSize;
  private final List<String> columnNames;
  private final CtidStateManager ctidStateManager;
  private final JdbcDatabase database;
  private final FileNodeHandler fileNodeHandler;
  private final String quoteString;
  private final String schemaName;
  private final CtidPostgresSourceOperations sourceOperations;
  private final Queue<Pair<Ctid, Ctid>> subQueriesPlan;
  private final String tableName;
  private final long tableSize;
  private final int maxTuple;
  private final boolean useTestPageSize;

  private AutoCloseableIterator<RowDataWithCtid> currentIterator;
  private Long lastKnownFileNode;
  private int numberOfTimesReSynced = 0;
  private boolean subQueriesInitialized = false;
  private final boolean tidRangeScanCapableDBServer;

  private final Instant startInstant;
  private Optional<Duration> cdcInitialLoadTimeout;
  private boolean isCdcSync;

  public InitialSyncCtidIterator(final CtidStateManager ctidStateManager,
                                 final JdbcDatabase database,
                                 final CtidPostgresSourceOperations sourceOperations,
                                 final String quoteString,
                                 final List<String> columnNames,
                                 final String schemaName,
                                 final String tableName,
                                 final long tableSize,
                                 final long blockSize,
                                 final int maxTuple,
                                 final FileNodeHandler fileNodeHandler,
                                 final boolean tidRangeScanCapableDBServer,
                                 final boolean useTestPageSize,
                                 final Instant startInstant,
                                 final Optional<Duration> cdcInitialLoadTimeout) {
    this.airbyteStream = AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);
    this.blockSize = blockSize;
    this.maxTuple = maxTuple;
    this.columnNames = columnNames;
    this.ctidStateManager = ctidStateManager;
    this.database = database;
    this.fileNodeHandler = fileNodeHandler;
    this.quoteString = quoteString;
    this.schemaName = schemaName;
    this.sourceOperations = sourceOperations;
    this.subQueriesPlan = new LinkedList<>();
    this.tableName = tableName;
    this.tableSize = tableSize;
    this.tidRangeScanCapableDBServer = tidRangeScanCapableDBServer;
    this.useTestPageSize = useTestPageSize;
    this.startInstant = startInstant;
    this.cdcInitialLoadTimeout = cdcInitialLoadTimeout;
    this.isCdcSync = isCdcSync(ctidStateManager);
  }

  @CheckForNull
  @Override
  protected RowDataWithCtid computeNext() {
    if (isCdcSync && cdcInitialLoadTimeout.isPresent()
        && Duration.between(startInstant, Instant.now()).compareTo(cdcInitialLoadTimeout.get()) > 0) {
      final String cdcInitialLoadTimeoutMessage = String.format(
          "Initial load for table %s has taken longer than %s hours, Canceling sync so that CDC replication can catch-up on subsequent attempt, and then initial snapshotting will resume",
          getAirbyteStream().get(), cdcInitialLoadTimeout.get().toHours());
      LOGGER.info(cdcInitialLoadTimeoutMessage);
      AirbyteTraceMessageUtility.emitAnalyticsTrace(cdcSnapshotForceShutdownMessage());
      throw new TransientErrorException(cdcInitialLoadTimeoutMessage);
    }
    try {
      if (!subQueriesInitialized) {
        initSubQueries();
        subQueriesInitialized = true;
      }

      if (currentIterator == null || !currentIterator.hasNext()) {
        do {
          final Optional<Long> mayBeLatestFileNode = PostgresQueryUtils.fileNodeForIndividualStream(database, airbyteStream, quoteString);
          if (mayBeLatestFileNode.isPresent()) {
            final Long latestFileNode = mayBeLatestFileNode.get();
            if (lastKnownFileNode != null) {
              if (!latestFileNode.equals(lastKnownFileNode)) {
                resetSubQueries(latestFileNode);
              } else {
                LOGGER.info("The latest file node {} for stream {} is equal to the last file node {} known to Airbyte.",
                    latestFileNode,
                    airbyteStream,
                    lastKnownFileNode);
              }
            }
            lastKnownFileNode = latestFileNode;
            fileNodeHandler.updateFileNode(airbyteStream, latestFileNode);
          } else {
            LOGGER.warn("Airbyte could not query the latest file node for stream {}. Continuing sync as usual.", airbyteStream);
          }

          if (currentIterator != null) {
            currentIterator.close();
          }

          if (subQueriesPlan.isEmpty()) {
            return endOfData();
          }

          final Pair<Ctid, Ctid> p = subQueriesPlan.remove();
          currentIterator = AutoCloseableIterators.fromStream(getStream(p), airbyteStream);
        } while (!currentIterator.hasNext());
      }

      return currentIterator.next();
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  private Stream<RowDataWithCtid> getStream(final Pair<Ctid, Ctid> p) throws SQLException {
    return database.unsafeQuery(
        connection -> getCtidStatement(connection, p.getLeft(), p.getRight()),
        sourceOperations::recordWithCtid);
  }

  private void initSubQueries() {
    if (useTestPageSize) {
      LOGGER.warn("Using test page size");
    }
    final CtidStatus currentCtidStatus = ctidStateManager.getCtidStatus(airbyteStream);
    subQueriesPlan.clear();

    subQueriesPlan.addAll(getQueryPlan(currentCtidStatus));
    lastKnownFileNode = currentCtidStatus != null ? currentCtidStatus.getRelationFilenode() : null;
  }

  private PreparedStatement getCtidStatement(final Connection connection,
                                             final Ctid lowerBound,
                                             final Ctid upperBound) {
    final PreparedStatement ctidStatement = tidRangeScanCapableDBServer ? createCtidQueryStatement(connection, lowerBound, upperBound)
        : createCtidLegacyQueryStatement(connection, lowerBound, upperBound);
    return ctidStatement;
  }

  private List<Pair<Ctid, Ctid>> getQueryPlan(final CtidStatus currentCtidStatus) {
    final List<Pair<Ctid, Ctid>> queryPlan = tidRangeScanCapableDBServer
        ? ctidQueryPlan((currentCtidStatus == null) ? Ctid.ZERO : Ctid.of(currentCtidStatus.getCtid()),
            tableSize, blockSize, QUERY_TARGET_SIZE_GB, useTestPageSize ? EIGHT_KB : GIGABYTE)
        : ctidLegacyQueryPlan((currentCtidStatus == null) ? Ctid.ZERO : Ctid.of(currentCtidStatus.getCtid()),
            tableSize, blockSize, QUERY_TARGET_SIZE_GB, useTestPageSize ? EIGHT_KB : GIGABYTE, maxTuple);
    return queryPlan;
  }

  private void resetSubQueries(final Long latestFileNode) {
    LOGGER.warn(
        "The latest file node {} for stream {} is not equal to the last file node {} known to Airbyte. Airbyte will sync this table from scratch again",
        latestFileNode,
        airbyteStream,
        lastKnownFileNode);
    if (numberOfTimesReSynced > MAX_ALLOWED_RESYNCS) {
      throw new RuntimeException("Airbyte has tried re-syncing stream " + airbyteStream + " more than " + MAX_ALLOWED_RESYNCS
          + " times but VACUUM is still happening in between the sync, Please reach out to the customer to understand their VACUUM frequency.");
    }
    subQueriesPlan.clear();
    subQueriesPlan.addAll(getQueryPlan(null));
    numberOfTimesReSynced++;
  }

  /**
   * Builds a plan for subqueries. Each query returning an approximate amount of data. Using
   * information about a table size and block (page) size.
   *
   * @param startCtid starting point
   * @param relationSize table size
   * @param blockSize page size
   * @param chunkSize required amount of data in each partition
   * @return a list of ctid that can be used to generate queries.
   */
  @VisibleForTesting
  static List<Pair<Ctid, Ctid>> ctidQueryPlan(final Ctid startCtid,
                                              final long relationSize,
                                              final long blockSize,
                                              final int chunkSize,
                                              final double dataSize) {
    final List<Pair<Ctid, Ctid>> chunks = new ArrayList<>();
    if (blockSize > 0 && chunkSize > 0 && dataSize > 0) {
      long lowerBound = startCtid.page;
      long upperBound;
      final double pages = dataSize / blockSize;
      final long eachStep = Math.max((long) pages * chunkSize, 1);
      LOGGER.info("Will read {} pages to get {}GB", eachStep, chunkSize);
      final long theoreticalLastPage = relationSize / blockSize;
      LOGGER.debug("Theoretical last page {}", theoreticalLastPage);
      upperBound = lowerBound + eachStep;

      if (upperBound > theoreticalLastPage) {
        chunks.add(Pair.of(startCtid, null));
      } else {
        chunks.add(Pair.of(Ctid.of(lowerBound, startCtid.tuple), Ctid.of(upperBound, 0)));
        while (upperBound < theoreticalLastPage) {
          lowerBound = upperBound;
          upperBound += eachStep;
          chunks.add(Pair.of(Ctid.of(lowerBound, 0), upperBound > theoreticalLastPage ? null : Ctid.of(upperBound, 0)));
        }
      }
    }
    // The last pair is (x,y) -> null to indicate an unbounded "WHERE ctid > (x,y)" query.
    // The actual last page is approximated. The last subquery will go until the end of table.
    return chunks;
  }

  static List<Pair<Ctid, Ctid>> ctidLegacyQueryPlan(final Ctid startCtid,
                                                    final long relationSize,
                                                    final long blockSize,
                                                    final int chunkSize,
                                                    final double dataSize,
                                                    final int tuplesInPage) {

    final List<Pair<Ctid, Ctid>> chunks = new ArrayList<>();
    if (blockSize > 0 && chunkSize > 0 && dataSize > 0 && tuplesInPage > 0) {
      // Start reading from one tuple after the last one that was read
      final Ctid firstCtid = Ctid.inc(startCtid, tuplesInPage);
      long lowerBound = firstCtid.page;
      long upperBound;
      final double pages = dataSize / blockSize;
      // cap each chunk at no more than 5m tuples
      final long eachStep = Math.max(
          Math.min((long) pages * chunkSize, MAX_TUPLES_IN_QUERY / tuplesInPage), 1);
      LOGGER.info("Will read {} pages on each query", eachStep);
      final long theoreticalLastPage = relationSize / blockSize;
      final long lastPage = (long) ((double) theoreticalLastPage * 1.1);
      LOGGER.info("Theoretical last page {}. will read until {}", theoreticalLastPage, lastPage);
      upperBound = lowerBound + eachStep;
      chunks.add((Pair.of(Ctid.of(lowerBound, firstCtid.tuple), Ctid.of(upperBound, tuplesInPage))));
      while (upperBound < lastPage) {
        lowerBound = upperBound + 1;
        upperBound += eachStep;
        chunks.add(Pair.of(Ctid.of(lowerBound, 1), Ctid.of(upperBound, tuplesInPage)));
      }
    }
    return chunks;
  }

  public PreparedStatement createCtidQueryStatement(final Connection connection,
                                                    final Ctid lowerBound,
                                                    final Ctid upperBound) {
    try {
      LOGGER.info("Preparing query for table: {}", tableName);
      final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, tableName,
          quoteString);
      final String wrappedColumnNames = RelationalDbQueryUtils.enquoteIdentifierList(columnNames, quoteString);
      if (upperBound != null) {
        final String sql = "SELECT ctid::text, %s FROM %s WHERE ctid > ?::tid AND ctid <= ?::tid".formatted(wrappedColumnNames, fullTableName);
        final PreparedStatement preparedStatement = connection.prepareStatement(sql);
        preparedStatement.setObject(1, lowerBound.toString());
        preparedStatement.setObject(2, upperBound.toString());
        LOGGER.info("Executing query for table {}: {} with bindings {} and {}", tableName, sql, lowerBound, upperBound);
        return preparedStatement;
      } else {
        final String sql = "SELECT ctid::text, %s FROM %s WHERE ctid > ?::tid".formatted(wrappedColumnNames, fullTableName);
        final PreparedStatement preparedStatement = connection.prepareStatement(sql);
        preparedStatement.setObject(1, lowerBound.toString());
        LOGGER.info("Executing query for table {}: {} with binding {}", tableName, sql, lowerBound);
        return preparedStatement;
      }
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  public PreparedStatement createCtidLegacyQueryStatement(final Connection connection,
                                                          final Ctid lowerBound,
                                                          final Ctid upperBound) {
    Preconditions.checkArgument(lowerBound != null, "Lower bound ctid expected");
    Preconditions.checkArgument(upperBound != null, "Upper bound ctid expected");
    try {
      LOGGER.info("Preparing query for table: {}", tableName);
      final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, tableName,
          quoteString);
      final String wrappedColumnNames = RelationalDbQueryUtils.enquoteIdentifierList(columnNames, quoteString);
      final String sql =
          "SELECT ctid::text, %s FROM %s WHERE ctid = ANY (ARRAY (SELECT FORMAT('(%%s,%%s)', page, tuple)::tid tid_addr FROM generate_series(?, ?) as page, generate_series(?,?) as tuple ORDER BY tid_addr))"
              .formatted(
                  wrappedColumnNames, fullTableName);
      final PreparedStatement preparedStatement = connection.prepareStatement(sql);
      preparedStatement.setLong(1, lowerBound.page);
      preparedStatement.setLong(2, upperBound.page);
      preparedStatement.setLong(3, lowerBound.tuple);
      preparedStatement.setLong(4, upperBound.tuple);
      LOGGER.info("Executing query for table {}: {}", tableName, preparedStatement);
      return preparedStatement;
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public Optional<AirbyteStreamNameNamespacePair> getAirbyteStream() {
    return Optional.of(airbyteStream);
  }

  @Override
  public void close() throws Exception {
    if (currentIterator != null) {
      currentIterator.close();
    }
  }

  private boolean isCdcSync(CtidStateManager initialLoadStateManager) {
    if (initialLoadStateManager instanceof CtidGlobalStateManager) {
      LOGGER.info("Running a cdc sync");
      return true;
    } else {
      LOGGER.info("Not running a cdc sync");
      return false;
    }
  }

}
