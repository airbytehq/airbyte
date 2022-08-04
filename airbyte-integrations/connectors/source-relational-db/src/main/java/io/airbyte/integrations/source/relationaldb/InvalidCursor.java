package io.airbyte.integrations.source.relationaldb;

import java.util.List;
import java.util.stream.Collectors;

public class InvalidCursor extends RuntimeException {

  public InvalidCursor(final List<Info> tablesWithInvalidCursor) {
    super("The following tables have invalid columns selected as cursor " + tablesWithInvalidCursor.stream().map(Info::toString)
        .collect(Collectors.joining(",")));
  }


  public static class Info {

    private final String tableName;
    private final String cursorColumnName;
    private final String cursorSqlType;

    public Info(final String tableName, final String cursorColumnName, final String cursorSqlType) {
      this.tableName = tableName;
      this.cursorColumnName = cursorColumnName;
      this.cursorSqlType = cursorSqlType;
    }

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
