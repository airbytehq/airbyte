/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import java.sql.SQLException;

/**
 * Utility class to define constants related to querying postgres.
 */
public class PostgresQueryUtils {

  public static final String NULL_CURSOR_VALUE_WITH_SCHEMA =
      """
        SELECT
          (EXISTS (SELECT FROM information_schema.columns WHERE table_schema = '%s' AND table_name = '%s' AND is_nullable = 'YES' AND column_name = '%s'))
        AND
          (EXISTS (SELECT from %s.\"%s\" where \"%s\" IS NULL LIMIT 1)) AS %s
      """;
  public static final String NULL_CURSOR_VALUE_NO_SCHEMA =
      """
      SELECT
        (EXISTS (SELECT FROM information_schema.columns WHERE table_name = '%s' AND is_nullable = 'YES' AND column_name = '%s'))
      AND
        (EXISTS (SELECT from \"%s\" where \"%s\" IS NULL LIMIT 1)) AS %s
      """;

  public static final String TABLE_ESTIMATE_QUERY =
      """
            SELECT (SELECT COUNT(*) FROM %s) AS %s,
            pg_relation_size('%s') AS %s;
      """;

  public static final String ROW_COUNT_RESULT_COL = "rowcount";

  public static final String TOTAL_BYTES_RESULT_COL = "totalbytes";


  public static String getFullyQualifiedTableNameWithQuoting(final String identifierQuoteString,
                                                             final String schemaName,
                                                             final String tableName)
      throws SQLException {
    final String quotedTableName = enquoteIdentifier(identifierQuoteString, tableName);
    return schemaName != null ? enquoteIdentifier(identifierQuoteString, schemaName) + "." + quotedTableName : quotedTableName;
  }

  public static String enquoteIdentifier(final String identifierQuoteString, final String identifier) {
    return identifierQuoteString + identifier + identifierQuoteString;
  }

}
