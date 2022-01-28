/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import org.jooq.JSONFormat;

public class JdbcUtils {

  private static final JdbcSourceOperations defaultSourceOperations = new JdbcSourceOperations();

  private static final JSONFormat defaultJSONFormat = new JSONFormat().recordFormat(JSONFormat.RecordFormat.OBJECT);

  public static JdbcSourceOperations getDefaultSourceOperations() {
    return defaultSourceOperations;
  }

  public static JSONFormat getDefaultJSONFormat() {
    return defaultJSONFormat;
  }

  public static String getFullyQualifiedTableName(final String schemaName, final String tableName) {
    return schemaName != null ? schemaName + "." + tableName : tableName;
  }

}
