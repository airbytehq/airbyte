/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.db;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import java.sql.SQLException;
import java.util.List;

public class PostgresUtils {

  public static PgLsn getLsn(final JdbcDatabase database) throws SQLException {
    // pg version >= 10. For versions < 10 use query select * from pg_current_xlog_location()
    final List<JsonNode> jsonNodes = database
        .bufferedResultSetQuery(conn -> conn.createStatement().executeQuery("select * from pg_current_wal_lsn()"),
            resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));

    Preconditions.checkState(jsonNodes.size() == 1);
    return PgLsn.fromPgString(jsonNodes.get(0).get("pg_current_wal_lsn").asText());
  }

}
