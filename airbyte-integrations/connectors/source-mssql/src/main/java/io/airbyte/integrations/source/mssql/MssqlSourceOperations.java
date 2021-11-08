package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import java.sql.Date;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.format.DateTimeFormatter;

public class MssqlSourceOperations extends JdbcSourceOperations {

  @Override
  protected void putBit(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    final boolean value = resultSet.getBoolean(index);
    node.put(columnName, value ? 1 : 0);
  }

  protected void putDate(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    final Date date = resultSet.getDate(index);
    String value = date.toLocalDate().format(DateTimeFormatter.ISO_LOCAL_DATE);
    node.put(columnName, value);
  }

  protected void putBinary(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    byte[] bytes = resultSet.getBytes(index);
    String value = new String(bytes);
    node.put(columnName, value);
  }

  protected void putTime(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    Timestamp timestamp = resultSet.getTimestamp(index);
    String value = timestamp.toLocalDateTime().format(DateTimeFormatter.ISO_LOCAL_TIME);
    node.put(columnName, value);
  }

}