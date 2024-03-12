/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsInAnyOrder;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.mysql.cj.MysqlType;
import io.airbyte.cdk.db.jdbc.DateTimeConverter;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.BaseImage;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.function.Function;
import java.util.function.IntFunction;
import org.junit.jupiter.api.Test;

public class MySqlSourceOperationsTest {

  @Test
  public void dateColumnAsCursor() throws SQLException {
    testImpl(
        "DATE",
        i -> LocalDate.of(2019, 1, i),
        DateTimeConverter::convertToDate,
        LocalDate::toString,
        MysqlType.DATE,
        DateTimeConverter.convertToDate(LocalDate.of(2019, 1, 1)),
        "2019-01-01T00:00:00Z");
  }

  @Test
  public void timeColumnAsCursor() throws SQLException {
    testImpl(
        "TIME",
        i -> LocalTime.of(20, i, 0),
        DateTimeConverter::convertToTime,
        LocalTime::toString,
        MysqlType.TIME,
        DateTimeConverter.convertToTime(LocalTime.of(20, 1, 0)),
        "1970-01-01T20:01:00Z");
  }

  @Test
  public void dateTimeColumnAsCursor() throws SQLException {
    testImpl(
        "DATETIME",
        i -> LocalDateTime.of(2019, i, 20, 3, 0, 0),
        DateTimeConverter::convertToTimestamp,
        LocalDateTime::toString,
        MysqlType.DATETIME,
        DateTimeConverter.convertToTimestamp(LocalDateTime.of(2019, 1, 20, 3, 0, 0)),
        "2019-01-20T03:00:00.000000");
  }

  @Test
  public void timestampColumnAsCursor() throws SQLException {
    testImpl(
        "TIMESTAMP",
        i -> Instant.ofEpochSecond(1660298508L).plusSeconds(i - 1),
        DateTimeConverter::convertToTimestampWithTimezone,
        r -> Timestamp.from(r).toString(),
        MysqlType.TIMESTAMP,
        DateTimeConverter.convertToTimestampWithTimezone(Instant.ofEpochSecond(1660298508L)),
        Instant.ofEpochSecond(1660298508L).toString());
  }

  private <T> void testImpl(
                            final String sqlType,
                            IntFunction<T> recordBuilder,
                            Function<T, String> airbyteRecordStringifier,
                            Function<T, String> sqlRecordStringifier,
                            MysqlType mysqlType,
                            String initialCursorFieldValue,
                            // Test to check backward compatibility for connectors created before PR
                            // https://github.com/airbytehq/airbyte/pull/15504
                            String backwardCompatibleInitialCursorFieldValue)
      throws SQLException {
    final var sqlSourceOperations = new MySqlSourceOperations();
    final String cursorColumn = "cursor_column";
    try (final var testdb = MySQLTestDatabase.in(BaseImage.MYSQL_8)
        .with("CREATE TABLE cursor_table (id INTEGER PRIMARY KEY, %s %s);", cursorColumn, sqlType)) {

      final List<JsonNode> expectedRecords = new ArrayList<>();
      for (int i = 1; i <= 4; i++) {
        final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
        jsonNode.put("id", i);
        final T cursorValue = recordBuilder.apply(i);
        jsonNode.put("cursor_column", airbyteRecordStringifier.apply(cursorValue));
        testdb.with("INSERT INTO cursor_table VALUES (%d, '%s');", i, sqlRecordStringifier.apply(cursorValue));
        if (i >= 2) {
          expectedRecords.add(jsonNode);
        }
      }

      try (final Connection connection = testdb.getContainer().createConnection("")) {
        final PreparedStatement preparedStatement = connection.prepareStatement(
            "SELECT * FROM " + testdb.getDatabaseName() + ".cursor_table WHERE " + cursorColumn + " > ?");
        for (final var initialValue : List.of(initialCursorFieldValue, backwardCompatibleInitialCursorFieldValue)) {
          sqlSourceOperations.setCursorField(preparedStatement, 1, mysqlType, initialValue);
          final List<JsonNode> actualRecords = new ArrayList<>();
          try (final ResultSet resultSet = preparedStatement.executeQuery()) {
            while (resultSet.next()) {
              final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
              for (int i = 1; i <= resultSet.getMetaData().getColumnCount(); i++) {
                sqlSourceOperations.copyToJsonField(resultSet, i, jsonNode);
              }
              actualRecords.add(jsonNode);
            }
          }
          assertThat(actualRecords, containsInAnyOrder(expectedRecords.toArray()));
        }
      }
    }
  }

}
