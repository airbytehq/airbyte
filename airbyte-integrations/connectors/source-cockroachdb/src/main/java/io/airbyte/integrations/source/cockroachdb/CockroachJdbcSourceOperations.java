package io.airbyte.integrations.source.cockroachdb;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Locale;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CockroachJdbcSourceOperations extends JdbcSourceOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(CockroachJdbcSourceOperations.class);

  private static final Map<String, String> specialCockroachDecimalTypeMap = Map.of();

  @Override
  protected void putBoolean(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    LOGGER.warn(resultSet.getMetaData().getColumnTypeName(index));
    LOGGER.warn(resultSet.getObject(index).toString());
    if (resultSet.getMetaData().getColumnTypeName(index).toLowerCase().contains("bit")) {
      node.put(columnName, resultSet.getByte(index));
    } else {
      node.put(columnName, resultSet.getBoolean(index));
    }
  }

  @Override
  protected void putNumber(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> resultSet.getDouble(index)));
  }

}
