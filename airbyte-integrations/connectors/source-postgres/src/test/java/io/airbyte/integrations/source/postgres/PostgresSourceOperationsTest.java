/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.DateTimeConverter;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.ContainerModifier;
import java.math.BigInteger;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class PostgresSourceOperationsTest {

  private final PostgresSourceOperations postgresSourceOperations = new PostgresSourceOperations();
  private PostgresTestDatabase testdb;

  private final String cursorColumn = "cursor_column";

  @BeforeEach
  public void init() {
    testdb = PostgresTestDatabase.in(BaseImage.POSTGRES_16, ContainerModifier.CONF);
  }

  @AfterEach
  public void tearDown() {
    testdb.close();
  }

  @Test
  public void numericColumnAsCursor() throws SQLException {
    final String tableName = "numeric_table";
    final String createTableQuery = String.format("CREATE TABLE %s(id INTEGER PRIMARY KEY, %s NUMERIC(38, 0));",
        tableName,
        cursorColumn);
    executeQuery(createTableQuery);
    final List<JsonNode> expectedRecords = new ArrayList<>();
    for (int i = 1; i <= 4; i++) {
      final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      jsonNode.put("id", i);
      final BigInteger cursorValue = BigInteger.valueOf(i * 10);
      jsonNode.put(cursorColumn, cursorValue);
      final String insertQuery = String.format("INSERT INTO %s VALUES (%s, %s);",
          tableName,
          i,
          cursorValue);
      executeQuery(insertQuery);
      expectedRecords.add(jsonNode);
    }

    final List<JsonNode> actualRecords = new ArrayList<>();
    try (final Connection connection = testdb.getContainer().createConnection("")) {
      final PreparedStatement preparedStatement = connection.prepareStatement(
          "SELECT * FROM " + tableName + " WHERE " + cursorColumn + " > ?");
      postgresSourceOperations.setCursorField(preparedStatement,
          1,
          PostgresType.NUMERIC,
          "0");

      try (final ResultSet resultSet = preparedStatement.executeQuery()) {
        final int columnCount = resultSet.getMetaData().getColumnCount();
        while (resultSet.next()) {
          final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
          for (int i = 1; i <= columnCount; i++) {
            postgresSourceOperations.copyToJsonField(resultSet, i, jsonNode);
          }
          actualRecords.add(jsonNode);
        }
      }
    }
    assertThat(actualRecords, containsInAnyOrder(expectedRecords.toArray()));
  }

  @Test
  public void timeColumnAsCursor() throws SQLException {
    final String tableName = "time_table";
    final String createTableQuery = String.format("CREATE TABLE %s(id INTEGER PRIMARY KEY, %s TIME);",
        tableName,
        cursorColumn);
    executeQuery(createTableQuery);
    final List<JsonNode> expectedRecords = new ArrayList<>();
    for (int i = 1; i <= 4; i++) {
      final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      jsonNode.put("id", i);
      final LocalTime cursorValue = LocalTime.of(20, i, 0);
      jsonNode.put(cursorColumn, DateTimeConverter.convertToTime(cursorValue));
      executeQuery("INSERT INTO " + tableName + " VALUES (" + i + ", '" + cursorValue + "');");
      expectedRecords.add(jsonNode);
    }

    final List<JsonNode> actualRecords = new ArrayList<>();
    try (final Connection connection = testdb.getContainer().createConnection("")) {
      final PreparedStatement preparedStatement = connection.prepareStatement(
          "SELECT * from " + tableName + " WHERE " + cursorColumn + " > ?");
      postgresSourceOperations.setCursorField(preparedStatement,
          1,
          PostgresType.TIME,
          DateTimeConverter.convertToTime(LocalTime.of(20, 0, 0)));

      try (final ResultSet resultSet = preparedStatement.executeQuery()) {
        final int columnCount = resultSet.getMetaData().getColumnCount();
        while (resultSet.next()) {
          final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
          for (int i = 1; i <= columnCount; i++) {
            postgresSourceOperations.copyToJsonField(resultSet, i, jsonNode);
          }
          actualRecords.add(jsonNode);
        }
      }
    }
    assertThat(actualRecords, containsInAnyOrder(expectedRecords.toArray()));
  }

  @Test
  public void testParseMoneyValue() {
    assertEquals("1000000.00", PostgresSourceOperations.parseMoneyValue("1000000.00"));
    assertEquals("1000000", PostgresSourceOperations.parseMoneyValue("$1000000"));
    assertEquals("-1000000.01", PostgresSourceOperations.parseMoneyValue("-1,000,000.01"));
    assertEquals("1000000.0", PostgresSourceOperations.parseMoneyValue("1,000,000.0"));
    assertEquals("1000000.0", PostgresSourceOperations.parseMoneyValue("1|000|000.0"));
    assertEquals("-1000000.001", PostgresSourceOperations.parseMoneyValue("-£1,000,000.001"));
  }

  protected void executeQuery(final String query) throws SQLException {
    try (final Connection connection = testdb.getContainer().createConnection("")) {
      connection.createStatement().execute(query);
    }
  }

}
