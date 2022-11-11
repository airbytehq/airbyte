package io.airbyte.integrations.source.relationaldb;

import java.util.List;
import java.util.stream.Collectors;

public class InvalidCursorException extends RuntimeException {

  public InvalidCursorException(final List<InvalidCursorInfo> tablesWithInvalidCursor) {
    super("The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering as a cursor. " + tablesWithInvalidCursor.stream().map(InvalidCursorInfo::toString)
        .collect(Collectors.joining(",")));
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
