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
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.sql.SQLException;
import java.util.Set;
import java.util.stream.Collectors;
import org.apache.commons.dbcp2.BasicDataSource;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;

class MssqlSourceTest {

  private static final String STREAM_NAME = "id_and_name";
  private static final AirbyteCatalog CATALOG = CatalogHelpers.createAirbyteCatalog(
      STREAM_NAME,
      Field.of("id", JsonSchemaPrimitive.NUMBER),
      Field.of("name", JsonSchemaPrimitive.STRING));
  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = CatalogHelpers.toDefaultConfiguredCatalog(CATALOG);
  private static final Set<AirbyteMessage> MESSAGES = Sets.newHashSet(
      new AirbyteMessage().withType(Type.RECORD)
          .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME).withData(Jsons.jsonNode(ImmutableMap.of("id", 1, "name", "picard")))),
      new AirbyteMessage().withType(Type.RECORD)
          .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME).withData(Jsons.jsonNode(ImmutableMap.of("id", 2, "name", "crusher")))),
      new AirbyteMessage().withType(Type.RECORD)
          .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME).withData(Jsons.jsonNode(ImmutableMap.of("id", 3, "name", "vash")))));

  private JsonNode configWithoutDbName;
  private JsonNode config;

  private static MSSQLServerContainer<?> db;
  private BasicDataSource connectionPool;

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
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER NOT NULL, name VARCHAR(200));");
      ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');");
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

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = new MssqlSource().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  @Test
  void testCheckSuccess() {
    final AirbyteConnectionStatus actual = new MssqlSource().check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @Test
  void testCheckFailure() {
    ((ObjectNode) config).put("password", "fake");
    final AirbyteConnectionStatus actual = new MssqlSource().check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.FAILED)
        .withMessage("Can't connect with provided configuration.");
    assertEquals(expected, actual);
  }

  @Test
  void testDiscover() throws Exception {
    final AirbyteCatalog actual = new MssqlSource().discover(config);
    assertEquals(CATALOG, actual);
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
  }

  @Test
  void testReadSuccess() throws Exception {
    final Set<AirbyteMessage> actualMessages = new MssqlSource().read(config, CONFIGURED_CATALOG, null).collect(Collectors.toSet());

    actualMessages.forEach(r -> {
      if (r.getRecord() != null) {
        r.getRecord().setEmittedAt(null);
      }
    });

    assertEquals(MESSAGES, actualMessages);
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testReadFailure() {
    final ConfiguredAirbyteStream spiedAbStream = spy(CONFIGURED_CATALOG.getStreams().get(0));
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(spiedAbStream));
    doThrow(new IllegalStateException()).when(spiedAbStream).getStream();

    final MssqlSource source = new MssqlSource();

    assertThrows(IllegalStateException.class, () -> source.read(config, catalog, null));
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
