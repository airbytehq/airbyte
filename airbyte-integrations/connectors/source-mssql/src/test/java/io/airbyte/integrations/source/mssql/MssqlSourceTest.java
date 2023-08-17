/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.catchThrowable;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.jooq.DSLContext;
import org.junit.jupiter.api.*;
import org.testcontainers.containers.MSSQLServerContainer;

class MssqlSourceTest {

  private static final String DB_NAME = "dbo";
  private static final String STREAM_NAME = "id_and_name";
  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(Lists.newArrayList(CatalogHelpers.createAirbyteStream(
      STREAM_NAME,
      DB_NAME,
      Field.of("id", JsonSchemaType.INTEGER),
      Field.of("name", JsonSchemaType.STRING),
      Field.of("born", JsonSchemaType.STRING))
      .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
      .withSourceDefinedPrimaryKey(List.of(List.of("id")))));

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
    final String dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

    try (final DSLContext dslContext = getDslContext(configWithoutDbName)) {
      final Database database = getDatabase(dslContext);
      database.query(ctx -> {
        ctx.fetch(String.format("CREATE DATABASE %s;", dbName));
        ctx.fetch(String.format("USE %s;", dbName));
        ctx.fetch("CREATE TABLE id_and_name(id INTEGER NOT NULL, name VARCHAR(200), born DATETIMEOFFSET(7));");
        ctx.fetch(
            "INSERT INTO id_and_name (id, name, born) VALUES (1,'picard', '2124-03-04T01:01:01Z'),  (2, 'crusher', '2124-03-04T01:01:01Z'), (3, 'vash', '2124-03-04T01:01:01Z');");
        return null;
      });
    }

    config = Jsons.clone(configWithoutDbName);
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, dbName);
    ((ObjectNode) config).put("ssl_method", Jsons.jsonNode(Map.of("ssl_method", "unencrypted")));
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
    try (final DSLContext dslContext = getDslContext(configWithoutDbName)) {
      final Database database = getDatabase(dslContext);
      database.query(ctx -> {
        ctx.fetch(String.format("USE %s;", config.get(JdbcUtils.DATABASE_KEY)));
        ctx.execute("ALTER TABLE id_and_name ADD CONSTRAINT i3pk PRIMARY KEY CLUSTERED (id);");
        ctx.execute("CREATE INDEX i1 ON id_and_name (id);");
        return null;
      });
    }

    final AirbyteCatalog actual = new MssqlSource().discover(config);
    assertEquals(CATALOG, actual);
  }

  @Test
  @Disabled("See https://github.com/airbytehq/airbyte/pull/23908#issuecomment-1463753684, enable once communication is out")
  public void testTableWithNullCursorValueShouldThrowException() throws Exception {
    try (final DSLContext dslContext = getDslContext(configWithoutDbName)) {
      final Database database = getDatabase(dslContext);
      database.query(ctx -> {
        ctx.fetch(String.format("USE %s;", config.get(JdbcUtils.DATABASE_KEY)));
        ctx.execute("ALTER TABLE id_and_name ALTER COLUMN id INTEGER NULL");
        ctx.execute("INSERT INTO id_and_name(id) VALUES (7), (8), (NULL)");
        return null;
      });

      ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream().withSyncMode(
          SyncMode.INCREMENTAL)
          .withCursorField(Lists.newArrayList("id"))
          .withDestinationSyncMode(DestinationSyncMode.APPEND)
          .withSyncMode(SyncMode.INCREMENTAL)
          .withStream(CatalogHelpers.createAirbyteStream(
              STREAM_NAME,
              DB_NAME,
              Field.of("id", JsonSchemaType.INTEGER),
              Field.of("name", JsonSchemaType.STRING),
              Field.of("born", JsonSchemaType.STRING))
              .withSupportedSyncModes(
                  Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
              .withSourceDefinedPrimaryKey(List.of(List.of("id"))));

      final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(
          Collections.singletonList(configuredAirbyteStream));

      final Throwable throwable = catchThrowable(() -> MoreIterators.toSet(
          new MssqlSource().read(config, catalog, null)));
      assertThat(throwable).isInstanceOf(ConfigErrorException.class)
          .hasMessageContaining(
              "The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering with no null values as a cursor. {tableName='dbo.id_and_name', cursorColumnName='id', cursorSqlType=INTEGER, cause=Cursor column contains NULL value}");
    }
  }

  private JsonNode getConfig(final MSSQLServerContainer<?> db) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .build());
  }

  private static DSLContext getDslContext(final JsonNode config) {
    return DSLContextFactory.create(DataSourceFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MSSQLSERVER.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%d;",
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt()),
        Map.of("encrypt", "false")), null);
  }

  public static Database getDatabase(final DSLContext dslContext) {
    // todo (cgardens) - rework this abstraction so that we do not have to pass a null into the
    // constructor. at least explicitly handle it, even if the impl doesn't change.
    return new Database(dslContext);
  }

}
