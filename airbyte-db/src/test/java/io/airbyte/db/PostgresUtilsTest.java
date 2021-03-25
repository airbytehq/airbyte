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

package io.airbyte.db;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.sql.SQLException;
import java.util.Map;
import org.apache.commons.dbcp2.BasicDataSource;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class PostgresUtilsTest {

  private static final Map<String, Long> TEST_LSNS = ImmutableMap.<String, Long>builder()
      .put("0/15E7A10", 22968848L)
      .put("0/15E7B08", 22969096L)
      .put("16/15E7B08", 94512249608L)
      .put("16/FFFFFFFF", 98784247807L)
      .put("7FFFFFFF/FFFFFFFF", Long.MAX_VALUE)
      .put("0/0", 0L)
      .build();

  private static PostgreSQLContainer<?> PSQL_DB;

  private BasicDataSource dataSource;

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();

  }

  @BeforeEach
  void setup() throws Exception {
    final String dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

    final JsonNode config = getConfig(PSQL_DB, dbName);

    final String initScriptName = "init_" + dbName.concat(".sql");
    MoreResources.writeResource(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource(initScriptName), PSQL_DB);

    dataSource = new BasicDataSource();
    dataSource.setDriverClassName("org.postgresql.Driver");
    dataSource.setUsername(config.get("username").asText());
    dataSource.setPassword(config.get("password").asText());
    dataSource.setUrl(String.format("jdbc:postgresql://%s:%s/%s",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText()));

    final JdbcDatabase defaultJdbcDatabase = new DefaultJdbcDatabase(dataSource);

    defaultJdbcDatabase.execute(connection -> {
      connection.createStatement().execute("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      connection.createStatement().execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
    });
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

  @Test
  void testGetLsn() throws SQLException {
    final JdbcDatabase database = new DefaultJdbcDatabase(dataSource);

    final String lsn1 = PostgresUtils.getLsn(database);
    assertNotNull(lsn1);
    assertTrue(PostgresUtils.lsnToLong(lsn1) > 0);

    database.execute(connection -> {
      connection.createStatement().execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
    });

    final String lsn2 = PostgresUtils.getLsn(database);
    assertNotNull(lsn2);
    assertTrue(PostgresUtils.lsnToLong(lsn2) > 0);

    assertTrue(PostgresUtils.compareLsns(lsn1, lsn2) < 0, "returned lsns are not ascending.");
  }

  @Test
  void testLsnToLong() {
    TEST_LSNS.forEach(
        (key, value) -> assertEquals(value, PostgresUtils.lsnToLong(key), String.format("Conversion failed. lsn: %s long value: %s", key, value)));
  }

  @Test
  void testLongToLsn() {
    TEST_LSNS.forEach(
        (key, value) -> assertEquals(key, PostgresUtils.longToLsn(value), String.format("Conversion failed. lsn: %s long value: %s", key, value)));
  }

}
