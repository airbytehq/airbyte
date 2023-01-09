/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.cockroachdb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.CockroachContainer;

class CockroachDbSourceTest {

  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "id_and_name";
  public static String COL_ROW_ID = "rowid";

  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          STREAM_NAME,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING),
          Field.of("power", JsonSchemaType.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("id"))),
      CatalogHelpers.createAirbyteStream(
          STREAM_NAME + "2",
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING),
          Field.of("power", JsonSchemaType.NUMBER),
          Field.of(COL_ROW_ID, JsonSchemaType.INTEGER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of(COL_ROW_ID))),
      CatalogHelpers.createAirbyteStream(
          "names",
          SCHEMA_NAME,
          Field.of("first_name", JsonSchemaType.STRING),
          Field.of("last_name", JsonSchemaType.STRING),
          Field.of("power", JsonSchemaType.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("first_name"), List.of("last_name")))));

  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = CatalogHelpers
      .toDefaultConfiguredCatalog(CATALOG);
  private static final Set<AirbyteMessage> ASCII_MESSAGES = Sets.newHashSet(
      createRecord(STREAM_NAME, SCHEMA_NAME,
          map("id", new BigDecimal("1.0"), "name", "goku", "power", Double.POSITIVE_INFINITY)),
      createRecord(STREAM_NAME, SCHEMA_NAME,
          map("id", new BigDecimal("2.0"), "name", "vegeta", "power", 9000.1)),
      createRecord(STREAM_NAME, SCHEMA_NAME, map("id", Double.NaN, "name", "piccolo", "power", Double.NEGATIVE_INFINITY)));

  private static final Set<AirbyteMessage> UTF8_MESSAGES = Sets.newHashSet(
      createRecord(STREAM_NAME, SCHEMA_NAME,
          ImmutableMap.of("id", 1L, "name", "\u2013 someutfstring")),
      createRecord(STREAM_NAME, SCHEMA_NAME, ImmutableMap.of("id", 2L, "name", "\u2215")));

  private static CockroachContainer PSQL_DB;

  private String dbName;

  @BeforeAll
  static void init() {
    PSQL_DB = new CockroachContainer("cockroachdb/cockroach:v20.2.18");
    PSQL_DB.start();
  }

  @BeforeEach
  void setup() throws Exception {
    dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

    final JsonNode config = getConfig(PSQL_DB, null);
    try (final DSLContext dslContext = getDslContext(config)) {
      final Database database = getDatabase(dslContext);
      database.query(ctx -> {
        ctx.fetch("CREATE DATABASE " + dbName + ";");
        ctx.fetch(
            "CREATE TABLE " + dbName + ".id_and_name(id NUMERIC(20, 10), name VARCHAR(200), power double precision, PRIMARY KEY (id));");
        ctx.fetch("CREATE INDEX i1 ON  " + dbName + ".id_and_name (id);");
        ctx.fetch(
            "INSERT INTO  " + dbName
                + ".id_and_name (id, name, power) VALUES (1,'goku', 'Infinity'),  (2, 'vegeta', 9000.1), ('NaN', 'piccolo', '-Infinity');");

        ctx.fetch(
            "CREATE TABLE  " + dbName + ".id_and_name2(id NUMERIC(20, 10), name VARCHAR(200), power double precision);");
        ctx.fetch(
            "INSERT INTO  " + dbName
                + ".id_and_name2 (id, name, power) VALUES (1,'goku', 'Infinity'),  (2, 'vegeta', 9000.1), ('NaN', 'piccolo', '-Infinity');");

        ctx.fetch(
            "CREATE TABLE  " + dbName
                + ".names(first_name VARCHAR(200), last_name VARCHAR(200), power double precision, PRIMARY KEY (first_name, last_name));");
        ctx.fetch(
            "INSERT INTO  " + dbName
                + ".names (first_name, last_name, power) VALUES ('san', 'goku', 'Infinity'),  ('prince', 'vegeta', 9000.1), ('piccolo', 'junior', '-Infinity');");
        return null;
      });
    }
  }

  private static Database getDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

  private static DSLContext getDslContext(final JsonNode config) {
    return DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()),
        SQLDialect.POSTGRES);
  }

  private JsonNode getConfig(final CockroachContainer psqlDb, final String dbName) {
    return getConfig(psqlDb, dbName, psqlDb.getUsername());
  }

  private JsonNode getConfig(final CockroachContainer psqlDb, final String dbName, final String username) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, Objects.requireNonNull(PSQL_DB.getContainerInfo()
            .getNetworkSettings()
            .getNetworks()
            .entrySet().stream()
            .findFirst()
            .get().getValue().getIpAddress()))
        .put(JdbcUtils.PORT_KEY, psqlDb.getExposedPorts().get(1))
        .put(JdbcUtils.DATABASE_KEY, dbName == null ? psqlDb.getDatabaseName() : dbName)
        .put(JdbcUtils.USERNAME_KEY, username)
        .put(JdbcUtils.PASSWORD_KEY, psqlDb.getPassword())
        .put(JdbcUtils.SSL_KEY, false)
        .build());
  }

  private JsonNode getConfig(final CockroachContainer psqlDb) {
    return getConfig(psqlDb, psqlDb.getDatabaseName());
  }

  @AfterAll
  static void cleanUp() {
    PSQL_DB.close();
  }

  @Test
  public void testCanReadUtf8() throws Exception {
    // force the db server to start with sql_ascii encoding to verify the tap can read UTF8 even when
    // default settings are in another encoding
    try (final CockroachContainer db = new CockroachContainer("cockroachdb/cockroach:v20.2.18")) {
      // .withCommand("postgres -c client_encoding=sql_ascii")
      db.start();
      final JsonNode config = getConfig(db);
      try (final DSLContext dslContext = getDslContext(config)) {
        final Database database = getDatabase(dslContext);
        database.query(ctx -> {
          ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
          ctx.fetch(
              "INSERT INTO id_and_name (id, name) VALUES (1,E'\\u2013 someutfstring'),  (2, E'\\u2215');");
          return null;
        });
      }

      final Set<AirbyteMessage> actualMessages = MoreIterators
          .toSet(new CockroachDbSource().read(config, CONFIGURED_CATALOG, null));
      setEmittedAtToNull(actualMessages);

      assertEquals(UTF8_MESSAGES, actualMessages);
    }
  }

  private static void setEmittedAtToNull(final Iterable<AirbyteMessage> messages) {
    messages.forEach(msg -> {
      if (msg.getRecord() != null) {
        msg.getRecord().setEmittedAt(null);
      }
    });
  }

  @Test
  void testDiscoverWithPk() throws Exception {
    final AirbyteCatalog actual = new CockroachDbSource().discover(getConfig(PSQL_DB, dbName));
    actual.getStreams().forEach(actualStream -> {
      final Optional<AirbyteStream> expectedStream =
          CATALOG.getStreams().stream()
              .filter(stream -> stream.getName().equals(actualStream.getName())).findAny();
      assertTrue(expectedStream.isPresent());
      assertEquals(expectedStream.get(), actualStream);
    });
  }

  @Test
  void testDiscoverWithPermissions() throws Exception {
    final JsonNode config = getConfig(PSQL_DB, dbName);
    try (final DSLContext dslContext = getDslContext(config)) {
      final Database database = getDatabase(dslContext);
      database.query(ctx -> {
        ctx.fetch(
            "CREATE USER cock;");
        ctx.fetch(
            "CREATE TABLE id_and_name_perm1(id NUMERIC(20, 10), name VARCHAR(200), power double precision, PRIMARY KEY (id));");
        ctx.fetch(
            "CREATE TABLE id_and_name_perm2(id NUMERIC(20, 10), name VARCHAR(200), power double precision, PRIMARY KEY (id));");
        ctx.fetch(
            "CREATE TABLE id_and_name_perm3(id NUMERIC(20, 10), name VARCHAR(200), power double precision, PRIMARY KEY (id));");
        ctx.fetch("grant all on database " + dbName + " to cock;");
        ctx.fetch("grant all on table " + dbName + ".public.id_and_name_perm1 to cock;");
        ctx.fetch("grant select on table " + dbName + ".public.id_and_name_perm2 to cock;");
        return null;
      });
    }

    final List<String> expected = List.of("id_and_name_perm1", "id_and_name_perm2");

    final AirbyteCatalog airbyteCatalog = new CockroachDbSource().discover(getConfig(PSQL_DB, dbName, "cock"));
    final List<String> actualNamesWithPermission =
        airbyteCatalog
            .getStreams()
            .stream()
            .map(AirbyteStream::getName)
            .toList();

    assertEquals(expected.size(), actualNamesWithPermission.size());
    assertEquals(expected, actualNamesWithPermission);
  }

  @Test
  void testReadSuccess() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_CATALOG.withStreams(CONFIGURED_CATALOG.getStreams().stream()
            .filter(s -> s.getStream().getName().equals(STREAM_NAME)).collect(
                Collectors.toList()));
    final Set<AirbyteMessage> actualMessages = MoreIterators
        .toSet(new CockroachDbSource().read(getConfig(PSQL_DB, dbName), configuredCatalog, null));
    setEmittedAtToNull(actualMessages);

    assertEquals(ASCII_MESSAGES, actualMessages);
  }

  private static AirbyteMessage createRecord(final String stream,
                                             final String namespace,
                                             final Map<Object, Object> data) {
    return new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withData(Jsons.jsonNode(data)).withStream(stream)
            .withNamespace(namespace));
  }

  private static Map<Object, Object> map(final Object... entries) {
    if (entries.length % 2 != 0) {
      throw new IllegalArgumentException("Entries must have even length");
    }

    return new HashMap<>() {

      {
        for (int i = 0; i < entries.length; i++) {
          put(entries[i++], entries[i]);
        }
      }

    };
  }

}
