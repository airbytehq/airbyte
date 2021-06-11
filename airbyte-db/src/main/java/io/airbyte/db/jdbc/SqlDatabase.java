package io.airbyte.db.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import java.sql.SQLException;
import java.util.stream.Stream;

public interface SqlDatabase extends AutoCloseable {

  void execute(String sql) throws SQLException;

  Stream<JsonNode> query(String sql, String... params) throws SQLException;

}
