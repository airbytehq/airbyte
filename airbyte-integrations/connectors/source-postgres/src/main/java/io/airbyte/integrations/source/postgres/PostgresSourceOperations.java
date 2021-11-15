package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.util.Collections;
import org.jooq.util.postgres.PostgresDataType;
import org.postgresql.util.PSQLException;

public class PostgresSourceOperations extends JdbcSourceOperations {

  @Override
  public JsonNode rowToJson(final ResultSet queryContext) throws SQLException {
    // the first call communicates with the database. after that the result is cached.
    final int columnCount = queryContext.getMetaData().getColumnCount();
    final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());

    for (int i = 1; i <= columnCount; i++) {
      // attempt to access the column. this allows us to know if it is null before we do type-specific
      // parsing. if it is null, we can move on. while awkward, this seems to be the agreed upon way of
      // checking for null values with jdbc.
      try {
        queryContext.getObject(i);
      } catch (PSQLException e) {
        // when a column is of type MONEY, getObject will throw exception
        // this is a bug that will not be fixed:
        // https://github.com/pgjdbc/pgjdbc/issues/425
        // https://github.com/pgjdbc/pgjdbc/issues/1835
        if (e.getMessage().contains("Bad value for type double")) {
          queryContext.getString(i);
        } else {
          throw e;
        }
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
      super.putString(node, columnName, resultSet, index);
    } else {
      super.putDouble(node, columnName, resultSet, index);
    }
  }

}
