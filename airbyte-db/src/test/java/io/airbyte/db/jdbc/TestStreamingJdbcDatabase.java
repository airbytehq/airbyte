/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.db.jdbc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.functional.CheckedConsumer;
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
    streamingJdbcDatabase = new StreamingJdbcDatabase(connectionPool, defaultJdbcDatabase, jdbcStreamingQueryConfiguration);

    defaultJdbcDatabase.execute(connection -> {
      connection.createStatement().execute("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      connection.createStatement().execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
    });
  }

  @AfterAll
  static void cleanUp() {
    PSQL_DB.close();
  }

  @SuppressWarnings("unchecked")
  @Test
  void testExecute() throws SQLException {
    CheckedConsumer<Connection, SQLException> queryExecutor = mock(CheckedConsumer.class);
    doNothing().when(defaultJdbcDatabase).execute(queryExecutor);

    streamingJdbcDatabase.execute(queryExecutor);

    verify(defaultJdbcDatabase).execute(queryExecutor);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testBufferedResultQuery() throws SQLException {
    doReturn(RECORDS_AS_JSON).when(defaultJdbcDatabase).bufferedResultSetQuery(any(), any());

    final List<JsonNode> actual = streamingJdbcDatabase.bufferedResultSetQuery(
        connection -> connection.createStatement().executeQuery("SELECT * FROM id_and_name;"),
        JdbcUtils::rowToJson);

    assertEquals(RECORDS_AS_JSON, actual);
    verify(defaultJdbcDatabase).bufferedResultSetQuery(any(), any());
  }

  @SuppressWarnings("unchecked")
  @Test
  void testResultSetQuery() throws SQLException {
    doReturn(RECORDS_AS_JSON.stream()).when(defaultJdbcDatabase).resultSetQuery(any(), any());

    final Stream<JsonNode> actual = streamingJdbcDatabase.resultSetQuery(
        connection -> connection.createStatement().executeQuery("SELECT * FROM id_and_name;"),
        JdbcUtils::rowToJson);
    final List<JsonNode> actualAsList = actual.collect(Collectors.toList());
    actual.close();

    assertEquals(RECORDS_AS_JSON, actualAsList);
    verify(defaultJdbcDatabase).resultSetQuery(any(), any());
  }

  @Test
  void testQuery() throws SQLException {
    // grab references to connection and prepared statement so we can verify the streaming config is
    // invoked.
    final AtomicReference<Connection> connection1 = new AtomicReference<>();
    final AtomicReference<PreparedStatement> ps1 = new AtomicReference<>();
    final Stream<JsonNode> actual = streamingJdbcDatabase.query(
        connection -> {
          connection1.set(connection);
          final PreparedStatement ps = connection.prepareStatement("SELECT * FROM id_and_name;");
          ps1.set(ps);
          return ps;
        },
        JdbcUtils::rowToJson);

    assertEquals(RECORDS_AS_JSON, actual.collect(Collectors.toList()));
    // verify that the query configuration is invoked.
    verify(jdbcStreamingQueryConfiguration).accept(connection1.get(), ps1.get());
  }

  private JsonNode getConfig(PostgreSQLContainer<?> psqlDb, String dbName) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", psqlDb.getHost())
        .put("port", psqlDb.getFirstMappedPort())
        .put("database", dbName)
        .put("username", psqlDb.getUsername())
        .put("password", psqlDb.getPassword())
        .build());
  }

}
