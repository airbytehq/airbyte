/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.dbcp2.BasicDataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class TestStreamingJdbcDatabase {

  private static final List<JsonNode> RECORDS_AS_JSON = Lists.newArrayList(
      Jsons.jsonNode(ImmutableMap.of("id", 1, "name", "picard")),
      Jsons.jsonNode(ImmutableMap.of("id", 2, "name", "crusher")),
      Jsons.jsonNode(ImmutableMap.of("id", 3, "name", "vash")));

  private static PostgreSQLContainer<?> PSQL_DB;

  private JdbcStreamingQueryConfiguration jdbcStreamingQueryConfiguration;
  private JdbcDatabase defaultJdbcDatabase;
  private JdbcDatabase streamingJdbcDatabase;
  private final JdbcSourceOperations sourceOperations = JdbcUtils.getDefaultSourceOperations();

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();

  }

  @BeforeEach
  void setup() throws Exception {
    jdbcStreamingQueryConfiguration = mock(JdbcStreamingQueryConfiguration.class);

    final String dbName = Strings.addRandomSuffix("db", "_", 10);

    final JsonNode config = getConfig(PSQL_DB, dbName);

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

    final BasicDataSource connectionPool = new BasicDataSource();
    connectionPool.setDriverClassName("org.postgresql.Driver");
    connectionPool.setUsername(config.get("username").asText());
    connectionPool.setPassword(config.get("password").asText());
    connectionPool.setUrl(String.format("jdbc:postgresql://%s:%s/%s",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText()));

    defaultJdbcDatabase = spy(new DefaultJdbcDatabase(connectionPool));
    streamingJdbcDatabase = new StreamingJdbcDatabase(connectionPool, JdbcUtils.getDefaultSourceOperations(), jdbcStreamingQueryConfiguration);

    defaultJdbcDatabase.execute(connection -> {
      connection.createStatement().execute("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      connection.createStatement().execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
    });
  }

  @AfterAll
  static void cleanUp() {
    PSQL_DB.close();
  }

  @Test
  void testQuery() throws SQLException {
    // grab references to connection and prepared statement so we can verify the streaming config is
    // invoked.
    final AtomicReference<Connection> connection1 = new AtomicReference<>();
    final AtomicReference<PreparedStatement> ps1 = new AtomicReference<>();
    final Stream<JsonNode> actual = streamingJdbcDatabase.unsafeQuery(
        connection -> {
          connection1.set(connection);
          final PreparedStatement ps = connection.prepareStatement("SELECT * FROM id_and_name;");
          ps1.set(ps);
          return ps;
        },
        sourceOperations::rowToJson);

    assertEquals(RECORDS_AS_JSON, actual.collect(Collectors.toList()));
    // verify that the query configuration is invoked.
    verify(jdbcStreamingQueryConfiguration).accept(connection1.get(), ps1.get());
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
