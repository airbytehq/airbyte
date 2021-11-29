package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.DataTypeUtils;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.Collections;

public class PostgresSourceOperations extends JdbcSourceOperations {

  @Override
  public JsonNode rowToJson(final ResultSet queryContext) throws SQLException {
    // the first call communicates with the database. after that the result is cached.
    final ResultSetMetaData metadata = queryContext.getMetaData();
    final int columnCount = metadata.getColumnCount();
    final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());

    for (int i = 1; i <= columnCount; i++) {
      // attempt to access the column. this allows us to know if it is null before we do type-specific
      // parsing. if it is null, we can move on. while awkward, this seems to be the agreed upon way of
      // checking for null values with jdbc.

      if (metadata.getColumnTypeName(i).equalsIgnoreCase("money")) {
        // when a column is of type MONEY, getObject will throw exception
        // this is a bug that will not be fixed:
        // https://github.com/pgjdbc/pgjdbc/issues/425
        // https://github.com/pgjdbc/pgjdbc/issues/1835
        queryContext.getString(i);
      } else {
        queryContext.getObject(i);
      }
      if (queryContext.wasNull()) {
        continue;
      }

      // convert to java types that will convert into reasonable json.
      setJsonField(queryContext, i, jsonNode);
    }

    return jsonNode;
  }

  @Override
  protected void putDouble(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    if (resultSet.getMetaData().getColumnTypeName(index).equals("money")) {
      putMoney(node, columnName, resultSet, index);
    } else {
      super.putDouble(node, columnName, resultSet, index);
    }
  }

  private void putMoney(final ObjectNode node, final String columnName, final ResultSet resultSet, final int index) throws SQLException {
    final String moneyValue = parseMoneyValue(resultSet.getString(index));
    node.put(columnName, DataTypeUtils.returnNullIfInvalid(() -> Double.valueOf(moneyValue), Double::isFinite));
  }

  /**
   * @return monetary value in numbers without the currency symbol or thousands separators.
   */
  @VisibleForTesting
  static String parseMoneyValue(final String moneyString) {
    return moneyString.replaceAll("[^\\d.-]", "");
  }

}
