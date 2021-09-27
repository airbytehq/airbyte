/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import java.sql.SQLException;
import java.util.List;

public class PostgresUtils {

  public static PgLsn getLsn(JdbcDatabase database) throws SQLException {
    // pg version 10+.
    final List<JsonNode> jsonNodes = database
        .bufferedResultSetQuery(conn -> conn.createStatement().executeQuery("SELECT pg_current_wal_lsn()"),
            resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));

    Preconditions.checkState(jsonNodes.size() == 1);
    return PgLsn.fromPgString(jsonNodes.get(0).get("pg_current_wal_lsn").asText());
  }

}
