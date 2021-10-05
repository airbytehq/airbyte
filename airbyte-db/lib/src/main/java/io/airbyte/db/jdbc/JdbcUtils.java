/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

public class JdbcUtils {

  private static final JdbcSourceOperations defaultSourceOperations = new JdbcSourceOperations();

  public static JdbcSourceOperations getDefaultSourceOperations() {
    return defaultSourceOperations;
  }

  public static String getFullyQualifiedTableName(String schemaName, String tableName) {
    return schemaName != null ? schemaName + "." + tableName : tableName;
  }

}
