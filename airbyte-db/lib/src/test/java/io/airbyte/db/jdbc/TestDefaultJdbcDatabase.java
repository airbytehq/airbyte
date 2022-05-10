/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Stream;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class TestDefaultJdbcDatabase {

  private static final List<JsonNode> RECORDS_AS_JSON = Lists.newArrayList(
      Jsons.jsonNode(ImmutableMap.of("id", 1, "name", "picard")),
      Jsons.jsonNode(ImmutableMap.of("id", 2, "name", "crusher")),
      Jsons.jsonNode(ImmutableMap.of("id", 3, "name", "vash")));

  private static PostgreSQLContainer<?> PSQL_DB;
  private final JdbcSourceOperations sourceOperations = JdbcUtils.getDefaultSourceOperations();
  private DataSource dataSource;
  private JdbcDatabase database;

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();
  }

  @AfterAll
  static void cleanUp() {
    PSQL_DB.close();
  }

  @BeforeEach
  void setup() throws Exception {
    final String dbName = Strings.addRandomSuffix("db", "_", 10);

    final JsonNode config = getConfig(PSQL_DB, dbName);
    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

    dataSource = getDataSourceFromConfig(config);
    database = new DefaultJdbcDatabase(dataSource);
    database.execute(connection -> {
      connection.createStatement().execute("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      connection.createStatement().execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
    });
  }

  @AfterEach
  void close() throws IOException {
    DataSourceFactory.close(dataSource);
  }

  @Test
  void testBufferedResultQuery() throws SQLException {
    final List<JsonNode> actual = database.bufferedResultSetQuery(
        connection -> connection.createStatement().executeQuery("SELECT * FROM id_and_name;"),
        sourceOperations::rowToJson);

    assertEquals(RECORDS_AS_JSON, actual);
  }

  @Test
  void testResultSetQuery() throws SQLException {
    try (final Stream<JsonNode> actual = database.unsafeResultSetQuery(
        connection -> connection.createStatement().executeQuery("SELECT * FROM id_and_name;"),
        sourceOperations::rowToJson)) {
      assertEquals(RECORDS_AS_JSON, actual.toList());
    }
  }

  @Test
  void testQuery() throws SQLException {
    final List<JsonNode> actual = database.queryJsons(
        connection -> connection.prepareStatement("SELECT * FROM id_and_name;"),
        sourceOperations::rowToJson);
    assertEquals(RECORDS_AS_JSON, actual);
  }

  private DataSource getDataSourceFromConfig(final JsonNode config) {
    return DataSourceFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get("host").asText(),
            config.get("port").asInt(),
            config.get("database").asText()));
  }

  private JsonNode getConfig(final PostgreSQLContainer<?> psqlDb, final String dbName) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", psqlDb.getHost())
        .put("port", psqlDb.getFirstMappedPort())
        .put("database", dbName)
        .put("username", psqlDb.getUsername())
        .put("password", psqlDb.getPassword())
        .build());
  }

}
