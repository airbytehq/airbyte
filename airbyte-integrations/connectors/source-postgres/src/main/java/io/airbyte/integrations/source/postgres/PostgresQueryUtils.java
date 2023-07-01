/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.postgres.xmin.XminStateManager.XMIN_STATE_VERSION;
import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class to define constants related to querying postgres
 */
public class PostgresQueryUtils {

  public record TableBlockSize(Long tableSize, Long blockSize) { }

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
   * Query returns the size table data takes on DB server disk (not incling any index or other metadata)
   * And the size of each page used in (page, tuple) ctid.
   * This helps us evaluate how many pages we need to read to traverse the entire table.
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

  public static Map<AirbyteStreamNameNamespacePair, Long> fileNodeForStreams(final JdbcDatabase database,
                                                                      final List<ConfiguredAirbyteStream> streams,
                                                                      final String quoteString) {
    final Map<AirbyteStreamNameNamespacePair, Long> fileNodes = new HashMap<>();
    streams.forEach(stream -> {
      final AirbyteStreamNameNamespacePair namespacePair =
          new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
      final long l = fileNodeForStreams(database, namespacePair, quoteString);
      fileNodes.put(namespacePair, l);
    });
    return fileNodes;
  }

  public static long fileNodeForStreams(final JdbcDatabase database, final AirbyteStreamNameNamespacePair stream, final String quoteString) {
    try {
      final String streamName = stream.getName();
      final String schemaName = stream.getNamespace();
      final String fullTableName =
          getFullyQualifiedTableNameWithQuoting(schemaName, streamName, quoteString);
      final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(
          conn -> conn.prepareStatement(CTID_FULL_VACUUM_REL_FILENODE_QUERY.formatted(fullTableName)).executeQuery(),
          resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
      Preconditions.checkState(jsonNodes.size() == 1);
      final long relationFilenode = jsonNodes.get(0).get("pg_relation_filenode").asLong();
      LOGGER.info("Relation filenode is for stream {} is {}", fullTableName, relationFilenode);
      return relationFilenode;
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  public static List<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair> streamsUnderVacuum(final JdbcDatabase database,
                                                                                                      final List<ConfiguredAirbyteStream> streams,
                                                                                                      final String quoteString) {
    final List<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair> streamsUnderVacuuming = new ArrayList<>();
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
      } catch (final SQLException e) {
        // Assume it's safe to progress and skip relation node and vaccuum validation
        LOGGER.warn("Failed to fetch vacuum for table {} info. Going to move ahead with the sync assuming it's safe", fullTableName, e);
      }
    });
    return streamsUnderVacuuming;
  }

  public static Map<AirbyteStreamNameNamespacePair, TableBlockSize> getTableBlockSizeForStream(final JdbcDatabase database,
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
}
