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

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.sql.SQLException;
import org.apache.commons.dbcp2.BasicDataSource;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class PostgresUtilsTest {

  private static PostgreSQLContainer<?> PSQL_DB;

  private BasicDataSource dataSource;

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();

  }

  @BeforeEach
  void setup() throws Exception {
    final String dbName = Strings.addRandomSuffix("db", "_", 10);

    final JsonNode config = getConfig(PSQL_DB, dbName);

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

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

    final PgLsn lsn1 = PostgresUtils.getLsn(database);
    assertNotNull(lsn1);
    assertTrue(lsn1.asLong() > 0);

    database.execute(connection -> {
      connection.createStatement().execute("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
    });

    final PgLsn lsn2 = PostgresUtils.getLsn(database);
    assertNotNull(lsn2);
    assertTrue(lsn2.asLong() > 0);

    assertTrue(lsn1.compareTo(lsn2) < 0, "returned lsns are not ascending.");
  }

}
