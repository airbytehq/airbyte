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
import io.airbyte.db.Databases;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterAll;
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

  private JsonNode config;
  private final JdbcSourceOperations sourceOperations = JdbcUtils.getDefaultSourceOperations();

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();

  }

  @BeforeEach
  void setup() throws Exception {
    final String dbName = Strings.addRandomSuffix("db", "_", 10);

    config = getConfig(PSQL_DB, dbName);

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

    final JdbcDatabase database = getDatabaseFromConfig(config);
    database.execute(connection -> {
      connection.createStatement().execute("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      connection.createStatement().execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
    });
    database.close();
  }

  @AfterAll
  static void cleanUp() {
    PSQL_DB.close();
  }

  @Test
  void testBufferedResultQuery() throws SQLException {
    final List<JsonNode> actual = getDatabaseFromConfig(config).bufferedResultSetQuery(
        connection -> connection.createStatement().executeQuery("SELECT * FROM id_and_name;"),
        sourceOperations::rowToJson);

    assertEquals(RECORDS_AS_JSON, actual);
  }

  @Test
  void testResultSetQuery() throws SQLException {
    final Stream<JsonNode> actual = getDatabaseFromConfig(config).resultSetQuery(
        connection -> connection.createStatement().executeQuery("SELECT * FROM id_and_name;"),
        sourceOperations::rowToJson);
    final List<JsonNode> actualAsList = actual.collect(Collectors.toList());
    actual.close();

    assertEquals(RECORDS_AS_JSON, actualAsList);
  }

  @Test
  void testQuery() throws SQLException {
    final Stream<JsonNode> actual = getDatabaseFromConfig(config).query(
        connection -> connection.prepareStatement("SELECT * FROM id_and_name;"),
        sourceOperations::rowToJson);

    assertEquals(RECORDS_AS_JSON, actual.collect(Collectors.toList()));
  }

  private JdbcDatabase getDatabaseFromConfig(final JsonNode config) {
    return Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        "org.postgresql.Driver");
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
