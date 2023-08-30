package io.airbyte.integrations.source.postgres.ctid;

import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils;
import io.airbyte.integrations.source.postgres.ctid.CtidPostgresSourceOperations.RowDataWithCtid;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
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

public class InitialSyncCtidIterator extends AbstractIterator<RowDataWithCtid> implements AutoCloseableIterator<RowDataWithCtid> {

  private static final Logger LOGGER = LoggerFactory.getLogger(InitialSyncCtidIterator.class);
  private static final int MAX_ALLOWED_RESYNCS = 5;
  private static final int QUERY_TARGET_SIZE_GB = 1;
  private static final double MEGABYTE = Math.pow(1024, 2);
  private static final double GIGABYTE = MEGABYTE * 1024;

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
  private AutoCloseableIterator<RowDataWithCtid> currentIterator;

  private Long lastKnownFileNode;
  private int numberOfTimesReSynced = 0;
  private boolean subQueriesInitialized = false;

  public InitialSyncCtidIterator(final CtidStateManager ctidStateManager,
      final JdbcDatabase database,
      final CtidPostgresSourceOperations sourceOperations,
      final String quoteString,
      final List<String> columnNames,
      final String schemaName,
      final String tableName,
      final long tableSize,
      final long blockSize,
      final FileNodeHandler fileNodeHandler) {
    this.airbyteStream = AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);
    this.blockSize = blockSize;
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
  }

  @CheckForNull
  @Override
  protected RowDataWithCtid computeNext() {
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
                LOGGER.info("The latest file node {} for stream {} is equal to the last known file node {} known to Airbyte.",
                    latestFileNode,
                    lastKnownFileNode,
                    airbyteStream);
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
        connection -> createCtidQueryStatement(connection, p.getLeft(), p.getRight()),
        sourceOperations::recordWithCtid);
  }

  private void initSubQueries() {
    final CtidStatus currentCtidStatus = ctidStateManager.getCtidStatus(airbyteStream);
    subQueriesPlan.clear();
    subQueriesPlan.addAll(ctidQueryPlan((currentCtidStatus == null) ? Ctid.of(0, 0) : Ctid.of(currentCtidStatus.getCtid()),
        tableSize, blockSize, QUERY_TARGET_SIZE_GB));
    lastKnownFileNode = currentCtidStatus != null ? currentCtidStatus.getRelationFilenode() : null;
  }

  private void resetSubQueries(final Long latestFileNode) {
    LOGGER.warn(
        "The latest file node {} for stream {} is not equal to the last known file node {} known to Airbyte. Airbyte will sync this table from scratch again",
        latestFileNode,
        lastKnownFileNode,
        airbyteStream);
    if (numberOfTimesReSynced > MAX_ALLOWED_RESYNCS) {
      throw new RuntimeException("Airbyte has tried re-syncing stream " + airbyteStream + " more than " + MAX_ALLOWED_RESYNCS
          + " times but VACUUM is still happening in between the sync, Please reach out to the customer to understand their VACUUM frequency.");
    }
    subQueriesPlan.clear();
    subQueriesPlan.addAll(ctidQueryPlan(Ctid.of(0, 0),
        tableSize, blockSize, QUERY_TARGET_SIZE_GB));
    numberOfTimesReSynced++;
  }

  /**
   * Builds a plan for subqueries. Each query returning an approximate amount of data. Using information about a table size and block (page) size.
   *
   * @param startCtid    starting point
   * @param relationSize table size
   * @param blockSize    page size
   * @param chunkSizeGB  required amount of data in each partition
   * @return a list of ctid that can be used to generate queries.
   */
  @VisibleForTesting
  static List<Pair<Ctid, Ctid>> ctidQueryPlan(final Ctid startCtid, final long relationSize, final long blockSize, final int chunkSizeGB) {
    final List<Pair<Ctid, Ctid>> chunks = new ArrayList<>();
    long lowerBound = startCtid.page;
    long upperBound;
    final double oneGigaPages = GIGABYTE / blockSize;
    final long eachStep = (long) oneGigaPages * chunkSizeGB;
    LOGGER.info("Will read {} pages to get {}GB", eachStep, chunkSizeGB);
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
    // The last pair is (x,y) -> null to indicate an unbounded "WHERE ctid > (x,y)" query.
    // The actual last page is approximated. The last subquery will go until the end of table.
    return chunks;
  }

  public PreparedStatement createCtidQueryStatement(
      final Connection connection,
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
        LOGGER.info("Executing query for table {}: {}", tableName, preparedStatement);
        return preparedStatement;
      } else {
        final String sql = "SELECT ctid::text, %s FROM %s WHERE ctid > ?::tid".formatted(wrappedColumnNames, fullTableName);
        final PreparedStatement preparedStatement = connection.prepareStatement(sql);
        preparedStatement.setObject(1, lowerBound.toString());
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
