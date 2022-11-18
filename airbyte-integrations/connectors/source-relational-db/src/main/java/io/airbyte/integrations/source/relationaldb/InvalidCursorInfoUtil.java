/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import java.util.List;
import java.util.stream.Collectors;

public class InvalidCursorInfoUtil {

  public static String getInvalidCursorConfigMessage(final List<InvalidCursorInfo> tablesWithInvalidCursor) {
    return "The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering as a cursor. "
        + tablesWithInvalidCursor.stream().map(InvalidCursorInfo::toString)
            .collect(Collectors.joining(","));
  }

  public record InvalidCursorInfo(String tableName, String cursorColumnName, String cursorSqlType) {

    @Override
    public String toString() {
      return "{" +
          "tableName='" + tableName + '\'' +
          ", cursorColumnName='" + cursorColumnName + '\'' +
          ", cursorSqlType=" + cursorSqlType +
          '}';
    }

  }

}
