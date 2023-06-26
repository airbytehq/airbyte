/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.createRecord;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.map;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.setEmittedAtToNull;
import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.catchThrowable;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.Database;
import io.airbyte.db.IncrementalUtils;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.integrations.source.relationaldb.state.StateManagerFactory;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.math.BigDecimal;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class PostgresSourceTest {

  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "id_and_name";
  private static final String STREAM_NAME_PRIVILEGES_TEST_CASE = "id_and_name_3";
  private static final String STREAM_NAME_WITH_QUOTES = "\"test_dq_table\"";
  private static final String STREAM_NAME_PRIVILEGES_TEST_CASE_VIEW = "id_and_name_3_view";
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
          Field.of("power", JsonSchemaType.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)),
      CatalogHelpers.createAirbyteStream(
          "names",
          SCHEMA_NAME,
          Field.of("first_name", JsonSchemaType.STRING),
          Field.of("last_name", JsonSchemaType.STRING),
          Field.of("power", JsonSchemaType.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("first_name"), List.of("last_name"))),
      CatalogHelpers.createAirbyteStream(
          STREAM_NAME_PRIVILEGES_TEST_CASE,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("id"))),
      CatalogHelpers.createAirbyteStream(
          STREAM_NAME_PRIVILEGES_TEST_CASE_VIEW,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("id")))));
  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = CatalogHelpers.toDefaultConfiguredCatalog(CATALOG);
  private static final ConfiguredAirbyteCatalog CONFIGURED_INCR_CATALOG = toIncrementalConfiguredCatalog(CATALOG);

  private static final Set<AirbyteMessage> ASCII_MESSAGES = Sets.newHashSet(
      createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("1.0"), "name", "goku", "power", null)),
      createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("2.0"), "name", "vegeta", "power", 9000.1)),
      createRecord(STREAM_NAME, SCHEMA_NAME, map("id", null, "name", "piccolo", "power", null)));

  private static final Set<AirbyteMessage> UTF8_MESSAGES = Sets.newHashSet(
      createRecord(STREAM_NAME, SCHEMA_NAME, ImmutableMap.of("id", 1, "name", "\u2013 someutfstring")),
      createRecord(STREAM_NAME, SCHEMA_NAME, ImmutableMap.of("id", 2, "name", "\u2215")));

  private static final Set<AirbyteMessage> DOUBLE_QUOTED_MESSAGES = Sets.newHashSet(
      createRecord(STREAM_NAME_WITH_QUOTES, SCHEMA_NAME, ImmutableMap.of("id", 1, "\"test_column\"", "test1")),
      createRecord(STREAM_NAME_WITH_QUOTES, SCHEMA_NAME, ImmutableMap.of("id", 2, "\"test_column\"", "test2")));

  private static final Set<AirbyteMessage> PRIVILEGE_TEST_CASE_EXPECTED_MESSAGES = Sets.newHashSet(
      createRecord(STREAM_NAME_PRIVILEGES_TEST_CASE, SCHEMA_NAME, ImmutableMap.of("id", 1, "name", "Zed")),
      createRecord(STREAM_NAME_PRIVILEGES_TEST_CASE, SCHEMA_NAME, ImmutableMap.of("id", 2, "name", "Jack")),
      createRecord(STREAM_NAME_PRIVILEGES_TEST_CASE, SCHEMA_NAME, ImmutableMap.of("id", 3, "name", "Antuan")),
      createRecord(STREAM_NAME_PRIVILEGES_TEST_CASE_VIEW, SCHEMA_NAME, ImmutableMap.of("id", 1, "name", "Zed")),
      createRecord(STREAM_NAME_PRIVILEGES_TEST_CASE_VIEW, SCHEMA_NAME, ImmutableMap.of("id", 2, "name", "Jack")),
      createRecord(STREAM_NAME_PRIVILEGES_TEST_CASE_VIEW, SCHEMA_NAME, ImmutableMap.of("id", 3, "name", "Antuan")));

  private static PostgreSQLContainer<?> PSQL_DB;

  private String dbName;

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();
  }

  @BeforeEach
  void setup() throws Exception {
    dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs.writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), PSQL_DB);

    final JsonNode config = getConfig(PSQL_DB, dbName);

    try (final DSLContext dslContext = getDslContext(config)) {
      final Database database = getDatabase(dslContext);
      database.query(ctx -> {
        ctx.fetch(
            "CREATE TABLE id_and_name(id NUMERIC(20, 10) NOT NULL, name VARCHAR(200) NOT NULL, power double precision NOT NULL, PRIMARY KEY (id));");
        ctx.fetch("CREATE INDEX i1 ON id_and_name (id);");
        ctx.fetch(
            "INSERT INTO id_and_name (id, name, power) VALUES (2, 'vegeta', 9000.1), (1,'goku', 'Infinity'), ('NaN', 'piccolo', '-Infinity');");

        ctx.fetch("CREATE TABLE id_and_name2(id NUMERIC(20, 10) NOT NULL, name VARCHAR(200) NOT NULL, power double precision NOT NULL);");
        ctx.fetch(
            "INSERT INTO id_and_name2 (id, name, power) VALUES (1,'goku', 'Infinity'),  (2, 'vegeta', 9000.1), ('NaN', 'piccolo', '-Infinity');");

        ctx.fetch(
            "CREATE TABLE names(first_name VARCHAR(200) NOT NULL, last_name VARCHAR(200) NOT NULL, power double precision NOT NULL, PRIMARY KEY (first_name, last_name));");
        ctx.fetch(
            "INSERT INTO names (first_name, last_name, power) VALUES ('san', 'goku', 'Infinity'),  ('prince', 'vegeta', 9000.1), ('piccolo', 'junior', '-Infinity');");
        return null;
      });
    }
  }

  private static DSLContext getDslContextWithSpecifiedUser(final JsonNode config, final String username, final String password) {
    return DSLContextFactory.create(
        username,
        password,
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()),
        SQLDialect.POSTGRES);
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

  private JsonNode getConfig(final PostgreSQLContainer<?> psqlDb, final String dbName) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, psqlDb.getHost())
        .put(JdbcUtils.PORT_KEY, psqlDb.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.SCHEMAS_KEY, List.of(SCHEMA_NAME))
        .put(JdbcUtils.USERNAME_KEY, psqlDb.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, psqlDb.getPassword())
        .put(JdbcUtils.SSL_KEY, false)
        .build());
  }

  private JsonNode getConfig(final PostgreSQLContainer<?> psqlDb, final String dbName, final String user, final String password) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, psqlDb.getHost())
        .put(JdbcUtils.PORT_KEY, psqlDb.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.SCHEMAS_KEY, List.of(SCHEMA_NAME))
        .put(JdbcUtils.USERNAME_KEY, user)
        .put(JdbcUtils.PASSWORD_KEY, password)
        .put(JdbcUtils.SSL_KEY, false)
        .build());
  }

  private JsonNode getConfig(final PostgreSQLContainer<?> psqlDb, final String user, final String password) {
    return getConfig(psqlDb, psqlDb.getDatabaseName(), user, password);
  }

  private JsonNode getConfig(final PostgreSQLContainer<?> psqlDb) {
    return getConfig(psqlDb, psqlDb.getDatabaseName());
  }

  @AfterAll
  static void cleanUp() {
    PSQL_DB.close();
  }

  @Test
  public void testCanReadTablesAndColumnsWithDoubleQuotes() throws Exception {
    try (final PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:13-alpine")) {
      db.start();

      final AirbyteCatalog airbyteCatalog = new AirbyteCatalog().withStreams(List.of(
          CatalogHelpers.createAirbyteStream(
              STREAM_NAME_WITH_QUOTES,
              SCHEMA_NAME,
              Field.of("id", JsonSchemaType.NUMBER),
              Field.of("\"test_column\"", JsonSchemaType.STRING))
              .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
              .withSourceDefinedPrimaryKey(List.of(List.of("id")))));

      final JsonNode config = getConfig(db);
      try (final DSLContext dslContext = getDslContext(config)) {
        final Database database = getDatabase(dslContext);

        database.query(ctx -> {
          ctx.fetch("CREATE TABLE \"\"\"test_dq_table\"\"\"(id INTEGER PRIMARY KEY,  \"\"\"test_column\"\"\" varchar);");
          ctx.fetch("INSERT INTO \"\"\"test_dq_table\"\"\" (id, \"\"\"test_column\"\"\") VALUES (1,'test1'),  (2, 'test2');");
          return null;
        });
      }
      final Set<AirbyteMessage> actualMessages =
          MoreIterators.toSet(new PostgresSource().read(config, CatalogHelpers.toDefaultConfiguredCatalog(airbyteCatalog), null));
      setEmittedAtToNull(actualMessages);

      assertEquals(DOUBLE_QUOTED_MESSAGES, actualMessages);
      db.stop();
    }
  }

  @Test
  public void testCanReadUtf8() throws Exception {
    // force the db server to start with sql_ascii encoding to verify the source can read UTF8 even when
    // default settings are in another encoding
    try (final PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:13-alpine").withCommand("postgres -c client_encoding=sql_ascii")) {
      db.start();
      final JsonNode config = getConfig(db);
      try (final DSLContext dslContext = getDslContext(config)) {
        final Database database = getDatabase(dslContext);
        database.query(ctx -> {
          ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
          ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,E'\\u2013 someutfstring'),  (2, E'\\u2215');");
          return null;
        });
      }

      final Set<AirbyteMessage> actualMessages = MoreIterators.toSet(new PostgresSource().read(config, CONFIGURED_CATALOG, null));
      setEmittedAtToNull(actualMessages);

      assertEquals(UTF8_MESSAGES, actualMessages);
      db.stop();
    }
  }

  @Test
  void testUserDoesntHasPrivilegesToSelectTable() throws Exception {
    try (final PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:13-alpine")) {
      db.start();
      final JsonNode config = getConfig(db);
      try (final DSLContext dslContext = getDslContext(config)) {
        final Database database = new Database(dslContext);
        database.query(ctx -> {
          ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
          ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'John'),  (2, 'Alfred'), (3, 'Alex');");
          ctx.fetch("CREATE USER test_user_3 password '132';");
          ctx.fetch("GRANT CONNECT ON DATABASE test TO test_user_3;");
          ctx.fetch("REVOKE ALL PRIVILEGES ON TABLE public.id_and_name FROM test_user_3");
          return null;
        });
      }
      try (final DSLContext dslContext = getDslContextWithSpecifiedUser(config, "test_user_3", "132")) {
        final Database database = new Database(dslContext);
        database.query(ctx -> {
          ctx.fetch("CREATE TABLE id_and_name_3(id INTEGER, name VARCHAR(200));");
          ctx.fetch("CREATE VIEW id_and_name_3_view(id, name) as\n"
              + "SELECT id_and_name_3.id,\n"
              + "       id_and_name_3.name\n"
              + "FROM id_and_name_3;\n"
              + "ALTER TABLE id_and_name_3_view\n"
              + "    owner TO test_user_3");
          ctx.fetch("INSERT INTO id_and_name_3 (id, name) VALUES (1,'Zed'),  (2, 'Jack'), (3, 'Antuan');");
          return null;
        });
      }
      final JsonNode anotherUserConfig = getConfig(db, "test_user_3", "132");
      final Set<AirbyteMessage> actualMessages = MoreIterators.toSet(new PostgresSource().read(anotherUserConfig, CONFIGURED_CATALOG, null));
      setEmittedAtToNull(actualMessages);
      assertEquals(6, actualMessages.size());
      assertEquals(PRIVILEGE_TEST_CASE_EXPECTED_MESSAGES, actualMessages);
      db.stop();
    }
  }

  @Test
  void testDiscoverWithPk() throws Exception {
    final AirbyteCatalog actual = new PostgresSource().discover(getConfig(PSQL_DB, dbName));
    actual.getStreams().forEach(actualStream -> {
      final Optional<AirbyteStream> expectedStream =
          CATALOG.getStreams().stream().filter(stream -> stream.getName().equals(actualStream.getName())).findAny();
      assertTrue(expectedStream.isPresent());
      assertEquals(expectedStream.get(), actualStream);
    });
  }

  @Test
  void testDiscoverRecursiveRolePermissions() throws Exception {
    try (final PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:13-alpine")) {
      db.start();
      final JsonNode config = getConfig(db);
      try (final DSLContext dslContext = getDslContext(config)) {
        final Database database = new Database(dslContext);
        database.query(ctx -> {
          ctx.fetch("CREATE TABLE id_and_name_7(id INTEGER, name VARCHAR(200));");
          ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");

          ctx.fetch("CREATE USER test_user_4 password '132';");

          ctx.fetch("CREATE ROLE airbyte LOGIN password 'airbyte';");
          ctx.fetch("CREATE ROLE read_only LOGIN password 'read_only';");
          ctx.fetch("CREATE ROLE intermediate LOGIN password 'intermediate';");

          ctx.fetch("CREATE ROLE access_nothing LOGIN password 'access_nothing';");

          ctx.fetch("GRANT intermediate TO airbyte;");
          ctx.fetch("GRANT read_only TO intermediate;");

          ctx.fetch("GRANT SELECT ON id_and_name, id_and_name_7 TO read_only;");
          ctx.fetch("GRANT airbyte TO test_user_4;");

          ctx.fetch("CREATE TABLE unseen(id INTEGER, name VARCHAR(200));");
          ctx.fetch("GRANT CONNECT ON DATABASE test TO test_user_4;");
          return null;
        });
      }
      try (final DSLContext dslContext = getDslContextWithSpecifiedUser(config, "test_user_4", "132")) {
        final Database database = new Database(dslContext);
        database.query(ctx -> {
          ctx.fetch("CREATE TABLE id_and_name_3(id INTEGER, name VARCHAR(200));");
          return null;
        });
      }
      AirbyteCatalog actual = new PostgresSource().discover(getConfig(db, "test_user_4", "132"));
      Set<String> tableNames = actual.getStreams().stream().map(stream -> stream.getName()).collect(Collectors.toSet());
      assertEquals(Sets.newHashSet("id_and_name", "id_and_name_7", "id_and_name_3"), tableNames);

      actual = new PostgresSource().discover(getConfig(db, "access_nothing", "access_nothing"));
      tableNames = actual.getStreams().stream().map(stream -> stream.getName()).collect(Collectors.toSet());
      assertEquals(Sets.newHashSet(), tableNames);
      db.stop();
    }
  }

  @Test
  void testDiscoverDifferentGrantAvailability() throws Exception {
    try (final PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:13-alpine")) {
      db.start();
      final JsonNode config = getConfig(db);
      try (final DSLContext dslContext = getDslContext(config)) {
        final Database database = new Database(dslContext);
        database.query(ctx -> {
          ctx.fetch("create table not_granted_table_name_1(column_1 integer);");
          ctx.fetch("create table not_granted_table_name_2(column_1 integer);");
          ctx.fetch("create table not_granted_table_name_3(column_1 integer);");
          ctx.fetch("create table table_granted_by_role(column_1 integer);");
          ctx.fetch("create table test_table_granted_directly(column_1 integer);");
          ctx.fetch("create table table_granted_by_role_with_options(column_1 integer);");
          ctx.fetch("create table test_table_granted_directly_with_options(column_1 integer);");

          ctx.fetch("create materialized view not_granted_mv_name_1 as SELECT not_granted_table_name_1.column_1 FROM not_granted_table_name_1;");
          ctx.fetch("create materialized view not_granted_mv_name_2 as SELECT not_granted_table_name_2.column_1 FROM not_granted_table_name_2;");
          ctx.fetch("create materialized view not_granted_mv_name_3 as SELECT not_granted_table_name_3.column_1 FROM not_granted_table_name_3;");
          ctx.fetch("create materialized view mv_granted_by_role as SELECT table_granted_by_role.column_1 FROM table_granted_by_role;");
          ctx.fetch(
              "create materialized view test_mv_granted_directly as SELECT test_table_granted_directly.column_1 FROM test_table_granted_directly;");
          ctx.fetch(
              "create materialized view mv_granted_by_role_with_options as SELECT table_granted_by_role_with_options.column_1 FROM table_granted_by_role_with_options;");
          ctx.fetch(
              "create materialized view test_mv_granted_directly_with_options as SELECT test_table_granted_directly_with_options.column_1 FROM test_table_granted_directly_with_options;");

          ctx.fetch("create view not_granted_view_name_1(column_1) as SELECT not_granted_table_name_1.column_1 FROM not_granted_table_name_1;");
          ctx.fetch("create view not_granted_view_name_2(column_1) as SELECT not_granted_table_name_2.column_1 FROM not_granted_table_name_2;");
          ctx.fetch("create view not_granted_view_name_3(column_1) as SELECT not_granted_table_name_3.column_1 FROM not_granted_table_name_3;");
          ctx.fetch("create view view_granted_by_role(column_1) as SELECT table_granted_by_role.column_1 FROM table_granted_by_role;");
          ctx.fetch(
              "create view test_view_granted_directly(column_1) as SELECT test_table_granted_directly.column_1 FROM test_table_granted_directly;");
          ctx.fetch(
              "create view view_granted_by_role_with_options(column_1) as SELECT table_granted_by_role_with_options.column_1 FROM table_granted_by_role_with_options;");
          ctx.fetch(
              "create view test_view_granted_directly_with_options(column_1) as SELECT test_table_granted_directly_with_options.column_1 FROM test_table_granted_directly_with_options;");

          ctx.fetch("create role test_role;");

          ctx.fetch("grant delete on not_granted_table_name_2 to test_role;");
          ctx.fetch("grant delete on not_granted_mv_name_2 to test_role;");
          ctx.fetch("grant delete on not_granted_view_name_2 to test_role;");

          ctx.fetch("grant select on table_granted_by_role to test_role;");
          ctx.fetch("grant select on mv_granted_by_role to test_role;");
          ctx.fetch("grant select on view_granted_by_role to test_role;");

          ctx.fetch("grant select on table_granted_by_role_with_options to test_role with grant option;");
          ctx.fetch("grant select on mv_granted_by_role_with_options to test_role with grant option;");
          ctx.fetch("grant select on view_granted_by_role_with_options to test_role with grant option;");

          ctx.fetch("create user new_test_user;");
          ctx.fetch("ALTER USER new_test_user WITH PASSWORD 'new_pass';");
          ctx.fetch("GRANT CONNECT ON DATABASE test TO new_test_user;");

          ctx.fetch("grant test_role to new_test_user;");

          ctx.fetch("grant delete on not_granted_table_name_3 to new_test_user;");
          ctx.fetch("grant delete on not_granted_mv_name_3 to new_test_user;");
          ctx.fetch("grant delete on not_granted_view_name_3 to new_test_user;");

          ctx.fetch("grant select on test_table_granted_directly to new_test_user;");
          ctx.fetch("grant select on test_mv_granted_directly to new_test_user;");
          ctx.fetch("grant select on test_view_granted_directly to new_test_user;");

          ctx.fetch("grant select on test_table_granted_directly_with_options to test_role with grant option;");
          ctx.fetch("grant select on test_mv_granted_directly_with_options to test_role with grant option;");
          ctx.fetch("grant select on test_view_granted_directly_with_options to test_role with grant option;");
          return null;
        });
      }

      final AirbyteCatalog actual = new PostgresSource().discover(getConfig(db, "new_test_user", "new_pass"));
      actual.getStreams().stream().forEach(airbyteStream -> {
        assertEquals(2, airbyteStream.getSupportedSyncModes().size());
        assertTrue(airbyteStream.getSupportedSyncModes().contains(SyncMode.FULL_REFRESH));
        assertTrue(airbyteStream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL));
      });
      final Set<String> tableNames = actual.getStreams().stream().map(stream -> stream.getName()).collect(Collectors.toSet());
      final Set<String> expectedVisibleNames = Sets.newHashSet(
          "table_granted_by_role",
          "table_granted_by_role_with_options",
          "test_table_granted_directly",
          "test_table_granted_directly_with_options",
          "mv_granted_by_role",
          "mv_granted_by_role_with_options",
          "test_mv_granted_directly",
          "test_mv_granted_directly_with_options",
          "test_view_granted_directly",
          "test_view_granted_directly_with_options",
          "view_granted_by_role",
          "view_granted_by_role_with_options");

      assertEquals(tableNames, expectedVisibleNames);

      db.stop();
    }
  }

  @Test
  void testReadSuccess() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_CATALOG.withStreams(CONFIGURED_CATALOG.getStreams().stream().filter(s -> s.getStream().getName().equals(STREAM_NAME)).collect(
            Collectors.toList()));
    final Set<AirbyteMessage> actualMessages = MoreIterators.toSet(new PostgresSource().read(getConfig(PSQL_DB, dbName), configuredCatalog, null));
    setEmittedAtToNull(actualMessages);

    assertEquals(ASCII_MESSAGES, actualMessages);
  }

  @Test
  void testReadIncrementalSuccess() throws Exception {
    final JsonNode config = getConfig(PSQL_DB, dbName);
    // We want to test ordering, so we can delete the NaN entry and add a 3.
    try (final DSLContext dslContext = getDslContext(config)) {
      final Database database = getDatabase(dslContext);
      database.query(ctx -> {
        ctx.fetch("DELETE FROM id_and_name WHERE id = 'NaN';");
        ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (3, 'gohan', 222.1);");
        return null;
      });
      final ConfiguredAirbyteCatalog configuredCatalog =
          CONFIGURED_INCR_CATALOG
              .withStreams(CONFIGURED_INCR_CATALOG.getStreams().stream().filter(s -> s.getStream().getName().equals(STREAM_NAME)).collect(
                  Collectors.toList()));
      final PostgresSource source = new PostgresSource();
      source.setStateEmissionFrequencyForDebug(1);
      final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(getConfig(PSQL_DB, dbName), configuredCatalog, null));
      setEmittedAtToNull(actualMessages);

      final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessage(actualMessages);

      setEmittedAtToNull(actualMessages);

      final Set<AirbyteMessage> expectedOutput = Sets.newHashSet(
          createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("1.0"), "name", "goku", "power", null)),
          createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("2.0"), "name", "vegeta", "power", 9000.1)),
          createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("3.0"), "name", "vegeta", "power", 222.1)));

      // Assert that the correct number of messages are emitted.
      assertEquals(actualMessages.size(), expectedOutput.size() + 2);
      assertThat(actualMessages.contains(expectedOutput));
      // Assert that the Postgres source is emitting records & state messages in the correct order.
      assertCorrectRecordOrderForIncrementalSync(actualMessages, "id", JsonSchemaPrimitive.NUMBER, configuredCatalog,
          new AirbyteStreamNameNamespacePair("id_and_name", "public"));

      final AirbyteStateMessage lastEmittedState = stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1);
      final JsonNode state = Jsons.jsonNode(List.of(lastEmittedState));

      database.query(ctx -> {
        ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (5, 'piccolo', 100.0);");
        return null;
      });
      // Incremental sync should only read one new message (where id = '5.0')
      final Set<AirbyteMessage> nextSyncMessages = MoreIterators.toSet(source.read(getConfig(PSQL_DB, dbName), configuredCatalog, state));
      setEmittedAtToNull(nextSyncMessages);

      // An extra state message is emitted, in addition to the record messages.
      assertEquals(nextSyncMessages.size(), 2);
      assertThat(nextSyncMessages.contains(createRecord(STREAM_NAME, SCHEMA_NAME, map("id", "5.0", "name", "piccolo", "power", 100.0))));
    }
  }

  /*
   * The messages that are emitted from an incremental sync should follow certain invariants. They
   * should : (i) Be emitted in increasing order of the defined cursor. (ii) A record that is emitted
   * after a state message should not have a cursor value less than a previously emitted state
   * message.
   */
  private void assertCorrectRecordOrderForIncrementalSync(final List<AirbyteMessage> messages,
                                                          final String cursorField,
                                                          final JsonSchemaPrimitive cursorType,
                                                          final ConfiguredAirbyteCatalog catalog,
                                                          final AirbyteStreamNameNamespacePair pair) {
    String prevRecordCursorValue = null;
    String prevStateCursorValue = null;
    for (final AirbyteMessage message : messages) {
      if (message.getType().equals(Type.RECORD)) {
        // Parse the cursor. Assert that (i) it's greater/equal to the prevRecordCursorValue and (ii)
        // greater than the previous state cursor value.
        final String cursorCandidate = message.getRecord().getData().get(cursorField).asText();
        assertThat(IncrementalUtils.compareCursors(prevRecordCursorValue, cursorCandidate, cursorType)).isLessThanOrEqualTo(0);
        assertThat(IncrementalUtils.compareCursors(prevStateCursorValue, cursorCandidate, cursorType)).isLessThanOrEqualTo(0);
        prevRecordCursorValue = cursorCandidate;
      } else if (message.getType().equals(Type.STATE)) {
        // Parse the state and the cursor value here. Assert that it is (i) greater than the previous state
        // emission value.
        final StateManager stateManager =
            StateManagerFactory.createStateManager(AirbyteStateType.LEGACY, List.of(message.getState()), catalog);
        final Optional<CursorInfo> cursorInfoOptional = stateManager.getCursorInfo(pair);
        final String cursorCandidate = cursorInfoOptional.get().getCursor();
        assertThat(IncrementalUtils.compareCursors(prevStateCursorValue, cursorCandidate, cursorType)).isLessThanOrEqualTo(0);
        prevStateCursorValue = cursorCandidate;
      }
    }
  }

  @Test
  void testIsCdc() {
    final JsonNode config = getConfig(PSQL_DB, dbName);

    assertFalse(PostgresUtils.isCdc(config));

    ((ObjectNode) config).set("replication_method", Jsons.jsonNode(ImmutableMap.of(
        "replication_slot", "slot",
        "publication", "ab_pub")));
    assertTrue(PostgresUtils.isCdc(config));
  }

  @Test
  void testGetUsername() {
    final String username = "airbyte-user";

    // normal host
    final JsonNode normalConfig = Jsons.jsonNode(Map.of(
        JdbcUtils.USERNAME_KEY, username,
        JdbcUtils.JDBC_URL_KEY, "jdbc:postgresql://airbyte.database.com:5432:airbyte"));
    assertEquals(username, PostgresSource.getUsername(normalConfig));

    // azure host
    final JsonNode azureConfig = Jsons.jsonNode(Map.of(
        JdbcUtils.USERNAME_KEY, username + "@airbyte",
        JdbcUtils.JDBC_URL_KEY, "jdbc:postgresql://airbyte.azure.com:5432:airbyte"));
    assertEquals(username, PostgresSource.getUsername(azureConfig));
  }

  @Test
  public void tableWithInvalidCursorShouldThrowException() throws Exception {
    try (final PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:13-alpine")) {
      db.start();
      final JsonNode config = getConfig(db);
      try (final DSLContext dslContext = getDslContext(config)) {
        final Database database = new Database(dslContext);
        final ConfiguredAirbyteStream tableWithInvalidCursorType = createTableWithInvalidCursorType(database);
        final ConfiguredAirbyteCatalog configuredAirbyteCatalog =
            new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(tableWithInvalidCursorType));

        final Throwable throwable = catchThrowable(() -> MoreIterators.toSet(new PostgresSource().read(config, configuredAirbyteCatalog, null)));
        assertThat(throwable).isInstanceOf(ConfigErrorException.class)
            .hasMessageContaining(
                "The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering with no null values as a cursor. {tableName='public.test_table', cursorColumnName='id', cursorSqlType=OTHER, cause=Unsupported cursor type}");
      } finally {
        db.stop();
      }
    }
  }

  private ConfiguredAirbyteStream createTableWithInvalidCursorType(final Database database) throws SQLException {
    database.query(ctx -> {
      ctx.fetch("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";");
      ctx.fetch("CREATE TABLE IF NOT EXISTS public.test_table(id uuid PRIMARY KEY DEFAULT uuid_generate_v4());");
      return null;
    });

    return new ConfiguredAirbyteStream().withSyncMode(SyncMode.INCREMENTAL)
        .withCursorField(Lists.newArrayList("id"))
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withSyncMode(SyncMode.INCREMENTAL)
        .withStream(CatalogHelpers.createAirbyteStream(
            "test_table",
            SCHEMA_NAME,
            Field.of("id", JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("id"))));

  }

  @Test
  void testJdbcUrlWithEscapedDatabaseName() {
    final JsonNode jdbcConfig = new PostgresSource().toDatabaseConfig(buildConfigEscapingNeeded());
    assertEquals(EXPECTED_JDBC_ESCAPED_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  private static final String EXPECTED_JDBC_ESCAPED_URL = "jdbc:postgresql://localhost:1111/db%2Ffoo?prepareThreshold=0&";

  private JsonNode buildConfigEscapingNeeded() {
    return Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 1111,
        JdbcUtils.USERNAME_KEY, "user",
        JdbcUtils.DATABASE_KEY, "db/foo",
        JdbcUtils.SSL_KEY, "false"));
  }

  @Test
  public void tableWithNullValueCursorShouldThrowException() throws SQLException {
    try (final PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:13-alpine")) {
      db.start();
      final JsonNode config = getConfig(db);
      try (final DSLContext dslContext = getDslContext(config)) {
        final Database database = new Database(dslContext);
        final ConfiguredAirbyteStream table = createTableWithNullValueCursor(database);
        final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(table));

        final Throwable throwable = catchThrowable(() -> MoreIterators.toSet(new PostgresSource().read(config, catalog, null)));
        assertThat(throwable).isInstanceOf(ConfigErrorException.class)
            .hasMessageContaining(
                "The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering with no null values as a cursor. {tableName='public.test_table_null_cursor', cursorColumnName='id', cursorSqlType=INTEGER, cause=Cursor column contains NULL value}");

      } finally {
        db.stop();
      }
    }
  }

  private ConfiguredAirbyteStream createTableWithNullValueCursor(final Database database) throws SQLException {
    database.query(ctx -> {
      ctx.fetch("CREATE TABLE IF NOT EXISTS public.test_table_null_cursor(id INTEGER NULL)");
      ctx.fetch("INSERT INTO public.test_table_null_cursor(id) VALUES (1), (2), (NULL)");
      return null;
    });

    return new ConfiguredAirbyteStream().withSyncMode(SyncMode.INCREMENTAL)
        .withCursorField(Lists.newArrayList("id"))
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withSyncMode(SyncMode.INCREMENTAL)
        .withStream(CatalogHelpers.createAirbyteStream(
            "test_table_null_cursor",
            SCHEMA_NAME,
            Field.of("id", JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("id"))));

  }

  @Test
  public void viewWithNullValueCursorShouldThrowException() throws SQLException {
    try (final PostgreSQLContainer<?> db = new PostgreSQLContainer<>("postgres:13-alpine")) {
      db.start();
      final JsonNode config = getConfig(db);
      try (final DSLContext dslContext = getDslContext(config)) {
        final Database database = new Database(dslContext);
        final ConfiguredAirbyteStream table = createViewWithNullValueCursor(database);
        final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(table));

        final Throwable throwable = catchThrowable(() -> MoreIterators.toSet(new PostgresSource().read(config, catalog, null)));
        assertThat(throwable).isInstanceOf(ConfigErrorException.class)
            .hasMessageContaining(
                "The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering with no null values as a cursor. {tableName='public.test_view_null_cursor', cursorColumnName='id', cursorSqlType=INTEGER, cause=Cursor column contains NULL value}");

      } finally {
        db.stop();
      }
    }
  }

  private ConfiguredAirbyteStream createViewWithNullValueCursor(final Database database) throws SQLException {
    database.query(ctx -> {
      ctx.fetch("CREATE TABLE IF NOT EXISTS public.test_table_null_cursor(id INTEGER NULL)");
      ctx.fetch("""
                CREATE VIEW test_view_null_cursor(id) as
                SELECT test_table_null_cursor.id
                FROM test_table_null_cursor
                """);
      ctx.fetch("INSERT INTO public.test_table_null_cursor(id) VALUES (1), (2), (NULL)");
      return null;
    });

    return new ConfiguredAirbyteStream().withSyncMode(SyncMode.INCREMENTAL)
        .withCursorField(Lists.newArrayList("id"))
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withSyncMode(SyncMode.INCREMENTAL)
        .withStream(CatalogHelpers.createAirbyteStream(
            "test_view_null_cursor",
            SCHEMA_NAME,
            Field.of("id", JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("id"))));

  }

  private static List<AirbyteStateMessage> extractStateMessage(final List<AirbyteMessage> messages) {
    return messages.stream().filter(r -> r.getType() == Type.STATE).map(AirbyteMessage::getState)
        .collect(Collectors.toList());
  }

  private static ConfiguredAirbyteCatalog toIncrementalConfiguredCatalog(final AirbyteCatalog catalog) {
    return new ConfiguredAirbyteCatalog()
        .withStreams(catalog.getStreams()
            .stream()
            .map(s -> toIncrementalConfiguredStream(s))
            .toList());
  }

  private static ConfiguredAirbyteStream toIncrementalConfiguredStream(final AirbyteStream stream) {
    return new ConfiguredAirbyteStream()
        .withStream(stream)
        .withSyncMode(SyncMode.INCREMENTAL)
        .withCursorField(List.of("id"))
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withPrimaryKey(new ArrayList<>());
  }

}
