package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import java.sql.Date;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.format.DateTimeFormatter;

public class MssqlSourceOperations extends JdbcSourceOperations {

  protected void putBinary(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    byte[] bytes = resultSet.getBytes(index);
    String value = new String(bytes);
    node.put(columnName, value);
  }

}