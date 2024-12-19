/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.legacy;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsInAnyOrder;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import java.sql.Connection;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class MssqlSourceOperationsTest {

  private final MssqlSourceOperations mssqlSourceOperations = new MssqlSourceOperations();

  private MsSQLTestDatabase testdb;

  private final String cursorColumn = "cursor_column";

  @BeforeEach
  public void init() {
    testdb = MsSQLTestDatabase.in(BaseImage.MSSQL_2022);
  }

  @AfterEach
  public void tearDown() {
    testdb.close();
  }

  @Test
  public void setDateTimeOffsetColumnAsCursor() throws SQLException {
    final String tableName = "datetimeoffset_table";
    final String createTableQuery = String.format("CREATE TABLE %s(id INTEGER PRIMARY KEY IDENTITY(1,1), %s DATETIMEOFFSET(7));",
        tableName,
        cursorColumn);
    executeQuery(createTableQuery);
    final List<JsonNode> expectedRecords = new ArrayList<>();
    for (int i = 1; i <= 4; i++) {
      final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      // Manually generate DATETIMEOFFSET data
      final String cursorValue = String.format("'2023-0%s-10T10:00:00.100000Z'", i, i * 10);
      jsonNode.put("id", i);
      // Remove single quotes from string since the date being retrieved will not have quotes
      jsonNode.put(cursorColumn, cursorValue.replaceAll("\'", ""));
      final String insertQuery = String.format("INSERT INTO %s (%s) VALUES (CAST(%s as DATETIMEOFFSET))", tableName, cursorColumn, cursorValue);

      executeQuery(insertQuery);
      expectedRecords.add(jsonNode);
    }
    final String cursorAnchorValue = "2023-01-01T00:00:00.000000+00:00";
    final List<JsonNode> actualRecords = new ArrayList<>();
    try (final Connection connection = testdb.getContainer().createConnection("")) {
      final PreparedStatement preparedStatement = connection.prepareStatement(
          "SELECT * from " + tableName + " WHERE " + cursorColumn + " > ?");
      mssqlSourceOperations.setCursorField(preparedStatement,
          1,
          JDBCType.TIMESTAMP_WITH_TIMEZONE,
          cursorAnchorValue);

      try (final ResultSet resultSet = preparedStatement.executeQuery()) {
        final int columnCount = resultSet.getMetaData().getColumnCount();
        while (resultSet.next()) {
          final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
          for (int i = 1; i <= columnCount; i++) {
            mssqlSourceOperations.copyToJsonField(resultSet, i, jsonNode);
          }
          actualRecords.add(jsonNode);
        }
      }
    }
    assertThat(actualRecords, containsInAnyOrder(expectedRecords.toArray()));
  }

  protected void executeQuery(final String query) throws SQLException {
    try (final Connection connection = testdb.getContainer().createConnection("")) {
      connection.createStatement().execute(query);
    }
  }

}
