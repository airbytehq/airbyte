/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.db.jdbc.streaming.FetchSizeConstants;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.atomic.AtomicReference;
import javax.sql.DataSource;
import org.elasticsearch.common.collect.Map;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class TestStreamingJdbcDatabase {

  private static PostgreSQLContainer<?> PSQL_DB;
  private final JdbcSourceOperations sourceOperations = JdbcUtils.getDefaultSourceOperations();
  private JdbcDatabase defaultJdbcDatabase;
  private JdbcDatabase streamingJdbcDatabase;

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
  void setup() {
    final String dbName = Strings.addRandomSuffix("db", "_", 10);

    final JsonNode config = getConfig(PSQL_DB, dbName);

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

    final DataSource connectionPool = DataSourceFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get("host").asText(),
            config.get("port").asInt(),
            config.get("database").asText()));

    defaultJdbcDatabase = spy(new DefaultJdbcDatabase(connectionPool));
    streamingJdbcDatabase = new StreamingJdbcDatabase(connectionPool, JdbcUtils.getDefaultSourceOperations(), AdaptiveStreamingQueryConfig::new);
  }

  @Test
  @Order(1)
  void testQuery() throws SQLException {
    defaultJdbcDatabase.execute(connection -> {
      connection.createStatement().execute(
          """
          DROP TABLE IF EXISTS id_and_name;
          CREATE TABLE id_and_name (id INTEGER, name VARCHAR(200));
          INSERT INTO id_and_name (id, name) VALUES (1, 'picard'),  (2, 'crusher'), (3, 'vash');
          """);
    });

    // grab references to connection and prepared statement, so we can verify the streaming config is
    // invoked.
    final AtomicReference<Connection> connection1 = new AtomicReference<>();
    final AtomicReference<PreparedStatement> ps1 = new AtomicReference<>();
    final List<JsonNode> actual = streamingJdbcDatabase.queryJsons(connection -> {
      connection1.set(connection);
      final PreparedStatement ps = connection.prepareStatement("SELECT * FROM id_and_name;");
      ps1.set(ps);
      return ps;
    }, sourceOperations::rowToJson);
    final List<JsonNode> expectedRecords = Lists.newArrayList(
        Jsons.jsonNode(Map.of("id", 1, "name", "picard")),
        Jsons.jsonNode(Map.of("id", 2, "name", "crusher")),
        Jsons.jsonNode(Map.of("id", 3, "name", "vash")));
    assertEquals(expectedRecords, actual);
  }

  /**
   * Test stream querying a table with 20 rows. Each row is 10 MB large. The table in this test must
   * contain more than {@code
   * FetchSizeConstants.INITIAL_SAMPLE_SIZE} rows. Otherwise, all rows will be fetched in the first
   * fetch, the fetch size won't be adjusted, and the test will fail.
   */
  @Order(2)
  @Test
  void testLargeRow() throws SQLException {
    defaultJdbcDatabase.execute(connection -> connection.createStatement()
        .execute(
            """
            DROP TABLE IF EXISTS id_and_name;
            CREATE TABLE id_and_name (id INTEGER, name TEXT);
            INSERT INTO id_and_name SELECT id, repeat('a', 10485760) as name from generate_series(1, 20) as id;
            """));

    final AtomicReference<Connection> connection1 = new AtomicReference<>();
    final AtomicReference<PreparedStatement> ps1 = new AtomicReference<>();
    final Set<Integer> fetchSizes = new HashSet<>();
    final List<JsonNode> actual = streamingJdbcDatabase.queryJsons(
        connection -> {
          connection1.set(connection);
          final PreparedStatement ps = connection.prepareStatement("SELECT * FROM id_and_name;");
          ps1.set(ps);
          return ps;
        },
        resultSet -> {
          fetchSizes.add(resultSet.getFetchSize());
          return sourceOperations.rowToJson(resultSet);
        });
    assertEquals(20, actual.size());

    // Two fetch sizes should be set on the result set, one is the initial sample size,
    // and the other is smaller than the initial value because of the large row.
    // This check assumes that FetchSizeConstants.TARGET_BUFFER_BYTE_SIZE = 200 MB.
    // Update this check if the buffer size constant is changed.
    assertEquals(2, fetchSizes.size());
    final List<Integer> sortedSizes = fetchSizes.stream().sorted().toList();
    assertTrue(sortedSizes.get(0) < FetchSizeConstants.INITIAL_SAMPLE_SIZE);
    assertEquals(FetchSizeConstants.INITIAL_SAMPLE_SIZE, sortedSizes.get(1));
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
