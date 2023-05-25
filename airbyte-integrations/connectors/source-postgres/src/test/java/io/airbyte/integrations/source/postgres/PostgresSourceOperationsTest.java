/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DateTimeConverter;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.util.HostPortResolver;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class PostgresSourceOperationsTest {

  private final PostgresSourceOperations postgresSourceOperations = new PostgresSourceOperations();
  private PostgreSQLContainer<?> container;
  private Database database;

  private final String cursorColumn = "cursor_column";

  @BeforeEach
  public void init() throws SQLException {
    container = new PostgreSQLContainer<>("postgres:14-alpine")
        .withCopyFileToContainer(MountableFile.forClasspathResource("postgresql.conf"),
            "/etc/postgresql/postgresql.conf")
        .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
    container.start();
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());
    final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(container))
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(container))
        .put(JdbcUtils.DATABASE_KEY, container.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put(JdbcUtils.SSL_KEY, false)
        .put("replication_method", replicationMethod)
        .build());

    final DSLContext dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            container.getHost(),
            container.getFirstMappedPort(),
            config.get(JdbcUtils.DATABASE_KEY).asText()),
        SQLDialect.POSTGRES);
    database = new Database(dslContext);
    database.query(ctx -> {
      ctx.execute(String.format("CREATE SCHEMA %S;", container.getDatabaseName()));
      return null;
    });
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
  public void numericColumnAsCursor() throws SQLException {
    final String tableName = container.getDatabaseName() + ".numeric_table";
    final String createTableQuery = String.format("CREATE TABLE %s(id INTEGER PRIMARY KEY, %s NUMERIC(38, 0));",
        tableName,
        cursorColumn);
    executeQuery(createTableQuery);
    final List<JsonNode> expectedRecords = new ArrayList<>();
    for (int i = 1; i <= 4; i++) {
      final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
      jsonNode.put("id", i);
      final long cursorValue = i * 10;
      jsonNode.put(cursorColumn, cursorValue);
      final String insertQuery = String.format("INSERT INTO %s VALUES (%s, %s);",
          tableName,
          i,
          cursorValue);
      executeQuery(insertQuery);
      expectedRecords.add(jsonNode);
    }

    final List<JsonNode> actualRecords = new ArrayList<>();
    try (final Connection connection = container.createConnection("")) {
      final PreparedStatement preparedStatement = connection.prepareStatement(
          "SELECT * from " + tableName + " WHERE " + cursorColumn + " > ?");
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
    final String tableName = container.getDatabaseName() + ".time_table";
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
    try (final Connection connection = container.createConnection("")) {
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
