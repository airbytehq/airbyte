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

package io.airbyte.integrations.source.mssql;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import javax.swing.*;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;

class MssqlSourceTest {

  private static final String STREAM_NAME = "dbo.id_and_name";
  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(Lists.newArrayList(CatalogHelpers.createAirbyteStream(
      STREAM_NAME,
      Field.of("id", JsonSchemaPrimitive.NUMBER),
      Field.of("name", JsonSchemaPrimitive.STRING),
      Field.of("born", JsonSchemaPrimitive.STRING))
      .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))));

  private JsonNode configWithoutDbName;
  private JsonNode config;

  private static MSSQLServerContainer<?> db;

  @BeforeAll
  static void init() {
    db = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-latest").acceptLicense();
    db.start();
  }

  // how to interact with the mssql test container manaully.
  // 1. exec into mssql container (not the test container container)
  // 2. /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P "A_Str0ng_Required_Password"
  @BeforeEach
  void setup() throws SQLException {
    configWithoutDbName = getConfig(db);
    final String dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

    final Database database = getDatabase(configWithoutDbName);
    database.query(ctx -> {
      ctx.fetch(String.format("CREATE DATABASE %s;", dbName));
      ctx.fetch(String.format("USE %s;", dbName));
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER NOT NULL, name VARCHAR(200), born DATETIMEOFFSET(7));");
      ctx.fetch(
          "INSERT INTO id_and_name (id, name, born) VALUES (1,'picard', '2124-03-04T01:01:01Z'),  (2, 'crusher', '2124-03-04T01:01:01Z'), (3, 'vash', '2124-03-04T01:01:01Z');");
      return null;
    });

    config = Jsons.clone(configWithoutDbName);
    ((ObjectNode) config).put("database", dbName);
  }

  @AfterAll
  static void cleanUp() {
    db.stop();
    db.close();
  }

  // if a column in mssql is used as a primary key and in a separate index the discover query returns
  // the column twice. we now de-duplicate it (pr: https://github.com/airbytehq/airbyte/pull/983).
  // this tests that this de-duplication is successful.
  @Test
  void testDiscoverWithPk() throws Exception {
    final Database database = getDatabase(configWithoutDbName);
    database.query(ctx -> {
      ctx.fetch(String.format("USE %s;", config.get("database")));
      ctx.execute("ALTER TABLE id_and_name ADD CONSTRAINT i3pk PRIMARY KEY CLUSTERED (id);");
      ctx.execute("CREATE INDEX i1 ON id_and_name (id);");
      return null;
    });

    final AirbyteCatalog actual = new MssqlSource().discover(config);
    assertEquals(CATALOG, actual);

    List<AirbyteMessage> read = new MssqlSource().read(config, CatalogHelpers.toDefaultConfiguredCatalog(actual), null).collect(Collectors.toList());

  }

  private JsonNode getConfig(MSSQLServerContainer<?> db) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .build());
  }

  private static Database getDatabase(JsonNode config) {
    // todo (cgardens) - rework this abstraction so that we do not have to pass a null into the
    // constructor. at least explicitly handle it, even if the impl doesn't change.
    return Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:sqlserver://%s:%s",
            config.get("host").asText(),
            config.get("port").asInt()),
        "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        null);
  }

}
