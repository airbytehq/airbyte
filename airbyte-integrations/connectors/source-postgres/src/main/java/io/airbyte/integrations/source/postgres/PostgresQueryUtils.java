/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.sql.SQLException;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class to define constants related to querying postgres
 */
public class PostgresQueryUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresQueryUtils.class);

  public static final String NULL_CURSOR_VALUE_WITH_SCHEMA_QUERY =
      """
        SELECT
          (EXISTS (SELECT FROM information_schema.columns WHERE table_schema = '%s' AND table_name = '%s' AND is_nullable = 'YES' AND column_name = '%s'))
        AND
          (EXISTS (SELECT from \"%s\".\"%s\" where \"%s\" IS NULL LIMIT 1)) AS %s
      """;
  public static final String NULL_CURSOR_VALUE_NO_SCHEMA_QUERY =
      """
      SELECT
        (EXISTS (SELECT FROM information_schema.columns WHERE table_name = '%s' AND is_nullable = 'YES' AND column_name = '%s'))
      AND
        (EXISTS (SELECT from \"%s\" where \"%s\" IS NULL LIMIT 1)) AS %s
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
        .withXminRawValue(result.get(XMIN_RAW_VALUE_COL).asLong());
  }

  public static void logFullVacuumStatus(final JdbcDatabase database, final ConfiguredAirbyteCatalog catalog, final String quoteString) {
    catalog.getStreams().forEach(stream -> {
      final String streamName = stream.getStream().getName();
      final String schemaName = stream.getStream().getNamespace();
      final String fullTableName =
          getFullyQualifiedTableNameWithQuoting(schemaName, streamName, quoteString);
      LOGGER.info("Full Vacuum information for {}", fullTableName);
      try {
        List<JsonNode> jsonNodes = database.bufferedResultSetQuery(
            conn -> conn.prepareStatement(CTID_FULL_VACUUM_REL_FILENODE_QUERY.formatted(fullTableName)).executeQuery(),
            resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
        Preconditions.checkState(jsonNodes.size() == 1);
        LOGGER.info("Relation filenode is {}", jsonNodes.get(0).get("pg_relation_filenode"));

        jsonNodes =
            database.bufferedResultSetQuery(conn -> conn.prepareStatement(CTID_FULL_VACUUM_IN_PROGRESS_QUERY.formatted(fullTableName)).executeQuery(),
                resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
        if (jsonNodes.size() == 0) {
          LOGGER.info("No full vacuum currently in progress");
        } else {
          Preconditions.checkState(jsonNodes.size() == 1);
          LOGGER.info("Full Vacuum currently in progress in {} phase", jsonNodes.get(0).get("phase"));
        }
      } catch (SQLException e) {
        LOGGER.warn("Failed to log full vacuum in progress. This warning shouldn't affect the sync and can be ignored", e);
      }
    });
  }

}
