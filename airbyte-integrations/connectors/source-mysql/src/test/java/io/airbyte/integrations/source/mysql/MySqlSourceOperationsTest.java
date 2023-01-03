/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.source.mysql.MySqlSource.DRIVER_CLASS;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsInAnyOrder;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.mysql.cj.MysqlType;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.jdbc.DateTimeConverter;
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
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

public class MySqlSourceOperationsTest {

  private final MySqlSourceOperations sqlSourceOperations = new MySqlSourceOperations();
  private MySQLContainer<?> container;
  private Database database;

  @BeforeEach
  public void init() {
    container = new MySQLContainer<>("mysql:8.0");
    container.start();
    database = new Database(DSLContextFactory.create(
        "root",
        "test",
        DRIVER_CLASS,
        String.format("jdbc:mysql://%s:%s",
            container.getHost(),
            container.getFirstMappedPort()),
        SQLDialect.MYSQL));
  }

  @AfterEach
  public void tearDown() {
    try {
      container.close();
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  @Test
  public void dateColumnAsCursor() throws SQLException {
    final String tableName = container.getDatabaseName() + ".table_with_date";
    final String cursorColumn = "cursor_column";
    executeQuery("CREATE TABLE " + tableName + "(id INTEGER PRIMARY KEY, " + cursorColumn + " DATE);");

    final List<JsonNode> expectedRecords = new ArrayList<>();
    for (int i = 1; i <= 4; i++) {
      final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      jsonNode.put("id", i);
      final LocalDate cursorValue = LocalDate.of(2019, 1, i);
      jsonNode.put("cursor_column", DateTimeConverter.convertToDate(cursorValue));
      executeQuery("INSERT INTO " + tableName + " VALUES (" + i + ", '" + cursorValue + "');");
      if (i >= 2) {
        expectedRecords.add(jsonNode);
      }
    }

    final List<JsonNode> actualRecords = new ArrayList<>();
    try (final Connection connection = container.createConnection("")) {
      final PreparedStatement preparedStatement = connection.prepareStatement(
          "SELECT * from " + tableName + " WHERE " + cursorColumn + " > ?");
      sqlSourceOperations.setCursorField(preparedStatement, 1, MysqlType.DATE, DateTimeConverter.convertToDate(LocalDate.of(2019, 1, 1)));

      try (final ResultSet resultSet = preparedStatement.executeQuery()) {
        while (resultSet.next()) {
          final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
          for (int i = 1; i <= resultSet.getMetaData().getColumnCount(); i++) {
            sqlSourceOperations.copyToJsonField(resultSet, i, jsonNode);
          }
          actualRecords.add(jsonNode);
        }
      }
    }
    assertThat(actualRecords, containsInAnyOrder(expectedRecords.toArray()));

    // Test to check backward compatibility for connectors created before PR
    // https://github.com/airbytehq/airbyte/pull/15504
    actualRecords.clear();
    try (final Connection connection = container.createConnection("")) {
      final PreparedStatement preparedStatement = connection.prepareStatement(
          "SELECT * from " + tableName + " WHERE " + cursorColumn + " > ?");
      sqlSourceOperations.setCursorField(preparedStatement, 1, MysqlType.DATE, "2019-01-01T00:00:00Z");

      try (final ResultSet resultSet = preparedStatement.executeQuery()) {
        while (resultSet.next()) {
          final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
          for (int i = 1; i <= resultSet.getMetaData().getColumnCount(); i++) {
            sqlSourceOperations.copyToJsonField(resultSet, i, jsonNode);
          }
          actualRecords.add(jsonNode);
        }
      }
    }
    assertThat(actualRecords, containsInAnyOrder(expectedRecords.toArray()));
  }

  @Test
  public void timeColumnAsCursor() throws SQLException {
    final String tableName = container.getDatabaseName() + ".table_with_time";
    final String cursorColumn = "cursor_column";
    executeQuery("CREATE TABLE " + tableName + "(id INTEGER PRIMARY KEY, " + cursorColumn + " TIME);");

    final List<JsonNode> expectedRecords = new ArrayList<>();
    for (int i = 1; i <= 4; i++) {
      final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      jsonNode.put("id", i);
      final LocalTime cursorValue = LocalTime.of(20, i, 0);
      jsonNode.put("cursor_column", DateTimeConverter.convertToTime(cursorValue));
      executeQuery("INSERT INTO " + tableName + " VALUES (" + i + ", '" + cursorValue + "');");
      if (i >= 2) {
        expectedRecords.add(jsonNode);
      }
    }

    final List<JsonNode> actualRecords = new ArrayList<>();
    try (final Connection connection = container.createConnection("")) {
      final PreparedStatement preparedStatement = connection.prepareStatement(
          "SELECT * from " + tableName + " WHERE " + cursorColumn + " > ?");
      sqlSourceOperations.setCursorField(preparedStatement, 1, MysqlType.TIME, DateTimeConverter.convertToTime(LocalTime.of(20, 1, 0)));

      try (final ResultSet resultSet = preparedStatement.executeQuery()) {
        while (resultSet.next()) {
          final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
          for (int i = 1; i <= resultSet.getMetaData().getColumnCount(); i++) {
            sqlSourceOperations.copyToJsonField(resultSet, i, jsonNode);
          }
          actualRecords.add(jsonNode);
        }
      }
    }
    assertThat(actualRecords, containsInAnyOrder(expectedRecords.toArray()));

    // Test to check backward compatibility for connectors created before PR
    // https://github.com/airbytehq/airbyte/pull/15504
    actualRecords.clear();
    try (final Connection connection = container.createConnection("")) {
      final PreparedStatement preparedStatement = connection.prepareStatement(
          "SELECT * from " + tableName + " WHERE " + cursorColumn + " > ?");
      sqlSourceOperations.setCursorField(preparedStatement, 1, MysqlType.TIME, "1970-01-01T20:01:00Z");

      try (final ResultSet resultSet = preparedStatement.executeQuery()) {
        while (resultSet.next()) {
          final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
          for (int i = 1; i <= resultSet.getMetaData().getColumnCount(); i++) {
            sqlSourceOperations.copyToJsonField(resultSet, i, jsonNode);
          }
          actualRecords.add(jsonNode);
        }
      }
    }
  }

  @Test
  public void dateTimeColumnAsCursor() throws SQLException {
    final String tableName = container.getDatabaseName() + ".table_with_datetime";
    final String cursorColumn = "cursor_column";
    executeQuery("CREATE TABLE " + tableName + "(id INTEGER PRIMARY KEY, " + cursorColumn + " DATETIME);");

    final List<JsonNode> expectedRecords = new ArrayList<>();
    for (int i = 1; i <= 4; i++) {
      final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      jsonNode.put("id", i);
      final LocalDateTime cursorValue = LocalDateTime.of(2019, i, 20, 3, 0, 0);
      jsonNode.put("cursor_column", DateTimeConverter.convertToTimestamp(cursorValue));
      executeQuery("INSERT INTO " + tableName + " VALUES (" + i + ", '" + cursorValue + "');");
      if (i >= 2) {
        expectedRecords.add(jsonNode);
      }
    }

    final List<JsonNode> actualRecords = new ArrayList<>();
    try (final Connection connection = container.createConnection("")) {
      final PreparedStatement preparedStatement = connection.prepareStatement(
          "SELECT * from " + tableName + " WHERE " + cursorColumn + " > ?");
      sqlSourceOperations.setCursorField(preparedStatement, 1, MysqlType.DATETIME,
          DateTimeConverter.convertToTimestamp(LocalDateTime.of(2019, 1, 20, 3, 0, 0)));

      try (final ResultSet resultSet = preparedStatement.executeQuery()) {
        while (resultSet.next()) {
          final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
          for (int i = 1; i <= resultSet.getMetaData().getColumnCount(); i++) {
            sqlSourceOperations.copyToJsonField(resultSet, i, jsonNode);
          }
          actualRecords.add(jsonNode);
        }
      }
    }
    assertThat(actualRecords, containsInAnyOrder(expectedRecords.toArray()));

    // Test to check backward compatibility for connectors created before PR
    // https://github.com/airbytehq/airbyte/pull/15504
    actualRecords.clear();
    try (final Connection connection = container.createConnection("")) {
      final PreparedStatement preparedStatement = connection.prepareStatement(
          "SELECT * from " + tableName + " WHERE " + cursorColumn + " > ?");
      sqlSourceOperations.setCursorField(preparedStatement, 1, MysqlType.DATETIME, "2019-01-20T03:00:00.000000Z");

      try (final ResultSet resultSet = preparedStatement.executeQuery()) {
        while (resultSet.next()) {
          final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
          for (int i = 1; i <= resultSet.getMetaData().getColumnCount(); i++) {
            sqlSourceOperations.copyToJsonField(resultSet, i, jsonNode);
          }
          actualRecords.add(jsonNode);
        }
      }
    }
    assertThat(actualRecords, containsInAnyOrder(expectedRecords.toArray()));
  }

  @Test
  public void timestampColumnAsCursor() throws SQLException {
    final String tableName = container.getDatabaseName() + ".table_with_timestamp";
    final String cursorColumn = "cursor_column";
    executeQuery("CREATE TABLE " + tableName + "(id INTEGER PRIMARY KEY, " + cursorColumn + " timestamp);");

    final List<JsonNode> expectedRecords = new ArrayList<>();
    for (int i = 1; i <= 4; i++) {
      final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      jsonNode.put("id", i);
      final Instant cursorValue = Instant.ofEpochSecond(1660298508L).plusSeconds(i - 1);
      jsonNode.put("cursor_column", DateTimeConverter.convertToTimestampWithTimezone(cursorValue));
      executeQuery("INSERT INTO " + tableName + " VALUES (" + i + ", '" + Timestamp.from(cursorValue) + "');");
      if (i >= 2) {
        expectedRecords.add(jsonNode);
      }
    }

    final List<JsonNode> actualRecords = new ArrayList<>();
    try (final Connection connection = container.createConnection("")) {
      final PreparedStatement preparedStatement = connection.prepareStatement(
          "SELECT * from " + tableName + " WHERE " + cursorColumn + " > ?");
      sqlSourceOperations.setCursorField(preparedStatement, 1, MysqlType.TIMESTAMP,
          DateTimeConverter.convertToTimestampWithTimezone(Instant.ofEpochSecond(1660298508L)));

      try (final ResultSet resultSet = preparedStatement.executeQuery()) {
        while (resultSet.next()) {
          final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
          for (int i = 1; i <= resultSet.getMetaData().getColumnCount(); i++) {
            sqlSourceOperations.copyToJsonField(resultSet, i, jsonNode);
          }
          actualRecords.add(jsonNode);
        }
      }
    }

    Assertions.assertEquals(3, actualRecords.size());

    // Test to check backward compatibility for connectors created before PR
    // https://github.com/airbytehq/airbyte/pull/15504
    actualRecords.clear();
    try (final Connection connection = container.createConnection("")) {
      final PreparedStatement preparedStatement = connection.prepareStatement(
          "SELECT * from " + tableName + " WHERE " + cursorColumn + " > ?");
      sqlSourceOperations.setCursorField(preparedStatement, 1, MysqlType.TIMESTAMP, Instant.ofEpochSecond(1660298508L).toString());

      try (final ResultSet resultSet = preparedStatement.executeQuery()) {
        while (resultSet.next()) {
          final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
          for (int i = 1; i <= resultSet.getMetaData().getColumnCount(); i++) {
            sqlSourceOperations.copyToJsonField(resultSet, i, jsonNode);
          }
          actualRecords.add(jsonNode);
        }
      }
    }
    Assertions.assertEquals(3, actualRecords.size());
  }

  protected void executeQuery(final String query) {
    try {
      database.query(
          ctx -> ctx
              .execute(query));
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

}
