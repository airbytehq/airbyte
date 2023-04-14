/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
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

  public static final String NUM_WRAPAROUND_COL = "num_wraparound";

  public static final String XMIN_XID_VALUE_COL = "xmin_xid_value";

  public static final String XMIN_RAW_VALUE_COL = "xmin_raw_value";

  public static final String ROW_COUNT_RESULT_COL = "rowcount";

  public static final String TOTAL_BYTES_RESULT_COL = "totalbytes";

  /**
   * Logs the current xmin status :
   * 1. The number of wraparounds the source DB has undergone. (These are the epoch bits in the xmin snapshot).
   * 2. The 32-bit xmin value associated with the xmin snapshot. This is the value that is ultimately written and recorded on every row.
   * 3. The raw value of the xmin snapshot (which is a combination of 1 and 2). If no wraparound has occurred, this should be the same as 2.
   */
  public static void logXminStatus(final JdbcDatabase database) throws SQLException {
    LOGGER.debug("xmin status query: {}", XMIN_STATUS_QUERY );
    final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.prepareStatement(XMIN_STATUS_QUERY).executeQuery(),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
    Preconditions.checkState(jsonNodes.size() == 1);
    final JsonNode result = jsonNodes.get(0);
    LOGGER.info(String.format("Xmin Status : {Number of wraparounds: %s, Xmin Transaction Value: %s, Xmin Raw Value: %s",
        result.get(NUM_WRAPAROUND_COL), result.get(XMIN_XID_VALUE_COL), result.get(XMIN_RAW_VALUE_COL)));
  }
}
