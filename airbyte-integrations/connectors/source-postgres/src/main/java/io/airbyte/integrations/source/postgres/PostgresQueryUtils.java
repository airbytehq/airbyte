/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.postgres.xmin.XminStateManager.XMIN_STATE_VERSION;
import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableList;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.postgres.ctid.CtidUtils.CtidStreams;
import io.airbyte.integrations.source.postgres.internal.models.CursorBasedStatus;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class to define constants related to querying postgres
 */
public class PostgresQueryUtils {

  public record TableBlockSize(Long tableSize, Long blockSize) {}
  public record ResultWithFailed<T>(T result, List<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair> failed) {}

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresQueryUtils.class);

  public static final String NULL_CURSOR_VALUE_WITH_SCHEMA_QUERY =
      """
        SELECT
          (EXISTS (SELECT FROM information_schema.columns WHERE table_schema = '%s' AND table_name = '%s' AND is_nullable = 'YES' AND column_name = '%s'))
        AND
          (EXISTS (SELECT from "%s"."%s" where "%s" IS NULL LIMIT 1)) AS %s
      """;
  public static final String NULL_CURSOR_VALUE_NO_SCHEMA_QUERY =
      """
      SELECT
        (EXISTS (SELECT FROM information_schema.columns WHERE table_name = '%s' AND is_nullable = 'YES' AND column_name = '%s'))
      AND
        (EXISTS (SELECT from "%s" where "%s" IS NULL LIMIT 1)) AS %s
      """;

  public static final String TABLE_ESTIMATE_QUERY =
      """
            SELECT (select reltuples::int8 as count from pg_class c JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace where nspname='%s' AND relname='%s') AS %s,
            pg_relation_size('%s') AS %s;
      """;

  /**
   * Creates query to understand the Xmin status.
   */
  public static final String XMIN_STATUS_QUERY =
      """
            select (txid_snapshot_xmin(txid_current_snapshot()) >> 32) AS num_wraparound,
            (txid_snapshot_xmin(txid_current_snapshot()) % (2^32)::bigint) AS xmin_xid_value,
            txid_snapshot_xmin(txid_current_snapshot()) AS xmin_raw_value;
      """;
  public static final String MAX_CURSOR_VALUE_QUERY =
      """
        SELECT %s FROM %s WHERE %s = (SELECT MAX(%s) FROM %s);
      """;

  public static final String CTID_FULL_VACUUM_IN_PROGRESS_QUERY =
      """
      SELECT phase FROM pg_stat_progress_cluster WHERE command = 'VACUUM FULL' AND relid=to_regclass('%s')::oid
      """;
  public static final String CTID_FULL_VACUUM_REL_FILENODE_QUERY =
      """
      SELECT pg_relation_filenode('%s')
      """;
  public static final String NUM_WRAPAROUND_COL = "num_wraparound";

  public static final String XMIN_XID_VALUE_COL = "xmin_xid_value";

  public static final String XMIN_RAW_VALUE_COL = "xmin_raw_value";

  public static final String ROW_COUNT_RESULT_COL = "rowcount";

  public static final String TOTAL_BYTES_RESULT_COL = "totalbytes";

  /**
   * Query returns the size table data takes on DB server disk (not incling any index or other
   * metadata) And the size of each page used in (page, tuple) ctid. This helps us evaluate how many
   * pages we need to read to traverse the entire table.
   */
  public static final String CTID_TABLE_BLOCK_SIZE =
      """
      WITH block_sz AS (SELECT current_setting('block_size')::int), rel_sz AS (select pg_relation_size('%s')) SELECT * from block_sz, rel_sz
      """;

  /**
   * Logs the current xmin status : 1. The number of wraparounds the source DB has undergone. (These
   * are the epoch bits in the xmin snapshot). 2. The 32-bit xmin value associated with the xmin
   * snapshot. This is the value that is ultimately written and recorded on every row. 3. The raw
   * value of the xmin snapshot (which is a combination of 1 and 2). If no wraparound has occurred,
   * this should be the same as 2.
   */
  public static XminStatus getXminStatus(final JdbcDatabase database) throws SQLException {
    LOGGER.debug("xmin status query: {}", XMIN_STATUS_QUERY);
    final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.prepareStatement(XMIN_STATUS_QUERY).executeQuery(),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
    Preconditions.checkState(jsonNodes.size() == 1);
    final JsonNode result = jsonNodes.get(0);
    return new XminStatus()
        .withNumWraparound(result.get(NUM_WRAPAROUND_COL).asLong())
        .withXminXidValue(result.get(XMIN_XID_VALUE_COL).asLong())
        .withXminRawValue(result.get(XMIN_RAW_VALUE_COL).asLong())
        .withVersion(XMIN_STATE_VERSION)
        .withStateType(StateType.XMIN);
  }

  /**
   * Iterates through each stream and find the max cursor value and the record count which has that
   * value based on each cursor field provided by the customer per stream This information is saved in
   * a Hashmap with the mapping being the AirbyteStreamNameNamespacepair -> CursorBasedStatus
   *
   * @param database the source db
   * @param streams streams to be synced
   * @param stateManager stream stateManager
   * @return
   */
  public static Map<AirbyteStreamNameNamespacePair, CursorBasedStatus> getCursorBasedSyncStatusForStreams(final JdbcDatabase database,
                                                                                                          final List<ConfiguredAirbyteStream> streams,
                                                                                                          final StateManager<AirbyteStateMessage, AirbyteStreamState> stateManager) {

    final Map<AirbyteStreamNameNamespacePair, CursorBasedStatus> cursorBasedStatusMap = new HashMap<>();
    streams.forEach(stream -> {
      try {
        final String name = stream.getStream().getName();
        final String namespace = stream.getStream().getNamespace();
        final Optional<CursorInfo> cursorInfoOptional =
            stateManager.getCursorInfo(new io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair(name, namespace));
        if (cursorInfoOptional.isEmpty()) {
          throw new RuntimeException(String.format("Stream %s was not provided with an appropriate cursor", stream.getStream().getName()));
        }

        LOGGER.info("Querying max cursor value for {}.{}", namespace, name);
        final String cursorField = cursorInfoOptional.get().getCursorField();
        final String cursorBasedSyncStatusQuery = String.format(MAX_CURSOR_VALUE_QUERY,
            cursorField,
            name,
            cursorField,
            cursorField,
            name);
        final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.prepareStatement(cursorBasedSyncStatusQuery).executeQuery(),
            resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
        final CursorBasedStatus cursorBasedStatus = new CursorBasedStatus();
        cursorBasedStatus.setStateType(StateType.CURSOR_BASED);
        cursorBasedStatus.setVersion(2L);
        cursorBasedStatus.setStreamName(name);
        cursorBasedStatus.setStreamNamespace(namespace);
        cursorBasedStatus.setCursorField(ImmutableList.of(cursorField));

        if (!jsonNodes.isEmpty()) {
          final JsonNode result = jsonNodes.get(0);
          cursorBasedStatus.setCursor(result.get(cursorField).asText());
          cursorBasedStatus.setCursorRecordCount((long) jsonNodes.size());
        }
        
        cursorBasedStatusMap.put(new AirbyteStreamNameNamespacePair(name, namespace), cursorBasedStatus);
      } catch (final SQLException e) {
        throw new RuntimeException(e);
      }
    });

    return cursorBasedStatusMap;
  }

  public static ResultWithFailed<Map<AirbyteStreamNameNamespacePair, Long>> fileNodeForStreams(final JdbcDatabase database,
                                                                             final List<ConfiguredAirbyteStream> streams,
                                                                             final String quoteString) {
    final Map<AirbyteStreamNameNamespacePair, Long> fileNodes = new HashMap<>();
    final List<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair> failedToQuery = new ArrayList<>();
    streams.forEach(stream -> {
      try {
        final AirbyteStreamNameNamespacePair namespacePair =
            new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
        final Optional<Long> fileNode = fileNodeForStreams(database, namespacePair, quoteString);
        fileNode.ifPresentOrElse(
            l -> fileNodes.put(namespacePair, l),
            () -> failedToQuery.add(io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(stream)));
      } catch (final Exception e) {
        LOGGER.warn("Failed to fetch relation node for {}.{} .", stream.getStream().getNamespace(), stream.getStream().getName(), e);
        failedToQuery.add(io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(stream));
      }
    });
    return new ResultWithFailed<>(fileNodes, failedToQuery);
  }

  public static Optional<Long> fileNodeForStreams(final JdbcDatabase database, final AirbyteStreamNameNamespacePair stream, final String quoteString)
      throws SQLException {
    final String streamName = stream.getName();
    final String schemaName = stream.getNamespace();
    final String fullTableName =
        getFullyQualifiedTableNameWithQuoting(schemaName, streamName, quoteString);
    final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(
        conn -> conn.prepareStatement(CTID_FULL_VACUUM_REL_FILENODE_QUERY.formatted(fullTableName)).executeQuery(),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
    Preconditions.checkState(jsonNodes.size() == 1);
    Long relationFilenode = null;
    if (!jsonNodes.get(0).isEmpty()) {
      relationFilenode = jsonNodes.get(0).get("pg_relation_filenode").asLong();
      LOGGER.info("Relation filenode is for stream {} is {}", fullTableName, relationFilenode);
    } else {
      LOGGER.debug("No filenode found for {}", fullTableName);
    }
    return Optional.ofNullable(relationFilenode);
  }

  public static ResultWithFailed<List<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair>> streamsUnderVacuum(final JdbcDatabase database,
                                                                                                      final List<ConfiguredAirbyteStream> streams,
                                                                                                      final String quoteString) {
    final List<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair> streamsUnderVacuuming = new ArrayList<>();
    final List<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair> failedToQuery = new ArrayList<>();
    streams.forEach(stream -> {
      final String streamName = stream.getStream().getName();
      final String schemaName = stream.getStream().getNamespace();
      final String fullTableName =
          getFullyQualifiedTableNameWithQuoting(schemaName, streamName, quoteString);
      try {
        final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(
            conn -> conn.prepareStatement(CTID_FULL_VACUUM_IN_PROGRESS_QUERY.formatted(fullTableName)).executeQuery(),
            resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
        if (jsonNodes.size() != 0) {
          Preconditions.checkState(jsonNodes.size() == 1);
          LOGGER.warn("Full Vacuum currently in progress for table {} in {} phase, the table will be skipped from syncing data", fullTableName,
              jsonNodes.get(0).get("phase"));
          streamsUnderVacuuming.add(io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(stream));
        }
      } catch (final Exception e) {
        // Assume it's safe to progress and skip relation node and vaccuum validation
        LOGGER.warn("Failed to fetch vacuum for table {} info. Going to move ahead with the sync assuming it's safe", fullTableName, e);
        failedToQuery.add(io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(stream));
      }
    });
    return new ResultWithFailed<>(streamsUnderVacuuming, failedToQuery);
  }

  public static Map<AirbyteStreamNameNamespacePair, TableBlockSize> getTableBlockSizeForStreams(final JdbcDatabase database,
                                                                                               final List<ConfiguredAirbyteStream> streams,
                                                                                               final String quoteString) {
    final Map<AirbyteStreamNameNamespacePair, TableBlockSize> tableBlockSizes = new HashMap<>();
    streams.forEach(stream -> {
      final AirbyteStreamNameNamespacePair namespacePair =
          new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
      final TableBlockSize sz = getTableBlockSizeForStream(database, namespacePair, quoteString);
      tableBlockSizes.put(namespacePair, sz);
    });
    return tableBlockSizes;

  }

  public static TableBlockSize getTableBlockSizeForStream(final JdbcDatabase database,
                                                          final AirbyteStreamNameNamespacePair stream,
                                                          final String quoteString) {
    try {
      final String streamName = stream.getName();
      final String schemaName = stream.getNamespace();
      final String fullTableName =
          getFullyQualifiedTableNameWithQuoting(schemaName, streamName, quoteString);
      final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(
          conn -> conn.prepareStatement(CTID_TABLE_BLOCK_SIZE.formatted(fullTableName)).executeQuery(),
          resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
      Preconditions.checkState(jsonNodes.size() == 1);
      final long relationSize = jsonNodes.get(0).get("pg_relation_size").asLong();
      final long blockSize = jsonNodes.get(0).get("current_setting").asLong();
      LOGGER.info("Stream {} relation size is {}. block size {}", fullTableName, relationSize, blockSize);
      return new TableBlockSize(relationSize, blockSize);
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Filter out streams that are currently under vacuum from being synced via Ctid
   *
   * @param streamsUnderVacuum streams that are currently under vacuum
   * @param ctidStreams preliminary streams to be synced via Ctid
   * @return ctid streams that are not under vacuum
   */
  public static List<ConfiguredAirbyteStream> filterStreamsUnderVacuumForCtidSync(final List<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair> streamsUnderVacuum,
                                                                                  final CtidStreams ctidStreams) {
    return streamsUnderVacuum.isEmpty() ? List.copyOf(ctidStreams.streamsForCtidSync())
        : ctidStreams.streamsForCtidSync().stream()
            .filter(c -> !streamsUnderVacuum.contains(io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(c)))
            .toList();
  }

}
