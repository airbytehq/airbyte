/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.createRecord;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.filterRecords;
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
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.IncrementalUtils;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManagerFactory;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.ContainerModifier;
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
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

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

  private PostgresTestDatabase testdb;

  @BeforeEach
  void setup() {
    testdb = PostgresTestDatabase.in(BaseImage.POSTGRES_16)
        .with("CREATE TABLE id_and_name(id NUMERIC(20, 10) NOT NULL, name VARCHAR(200) NOT NULL, power double precision NOT NULL, PRIMARY KEY (id));")
        .with("CREATE INDEX i1 ON id_and_name (id);")
        .with("INSERT INTO id_and_name (id, name, power) VALUES (1,'goku', 'Infinity'), (2, 'vegeta', 9000.1), ('NaN', 'piccolo', '-Infinity');")
        .with("CREATE TABLE id_and_name2(id NUMERIC(20, 10) NOT NULL, name VARCHAR(200) NOT NULL, power double precision NOT NULL);")
        .with("INSERT INTO id_and_name2 (id, name, power) VALUES (1,'goku', 'Infinity'),  (2, 'vegeta', 9000.1), ('NaN', 'piccolo', '-Infinity');")
        .with(
            "CREATE TABLE names(first_name VARCHAR(200) NOT NULL, last_name VARCHAR(200) NOT NULL, power double precision NOT NULL, PRIMARY KEY (first_name, last_name));")
        .with("INSERT INTO names (first_name, last_name, power) VALUES ('san', 'goku', 'Infinity'),  ('prince', " +
            "'vegeta', 9000.1), ('piccolo', 'junior', '-Infinity');");
  }

  @AfterEach
  void tearDown() {
    testdb.close();
    if (postgresSource != null) {
      postgresSource.close();
    }
    postgresSource = null;
  }

  private PostgresSource postgresSource = null;

  protected PostgresSource source() {
    if (postgresSource != null) {
      postgresSource.close();
    }
    postgresSource = new PostgresSource();
    return postgresSource;
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

  private JsonNode getConfig() {
    return getConfig(testdb.getUserName(), testdb.getPassword());
  }

  private JsonNode getConfig(final String user, final String password) {
    return getConfig(testdb.getDatabaseName(), user, password);
  }

  private JsonNode getConfig(final String dbName, final String user, final String password) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, testdb.getContainer().getHost())
        .put(JdbcUtils.PORT_KEY, testdb.getContainer().getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.SCHEMAS_KEY, List.of(SCHEMA_NAME))
        .put(JdbcUtils.USERNAME_KEY, user)
        .put(JdbcUtils.PASSWORD_KEY, password)
        .put(JdbcUtils.SSL_KEY, false)
        .put(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .build());
  }

  @Test
  public void testCanReadTablesAndColumnsWithDoubleQuotes() throws Exception {
    final AirbyteCatalog airbyteCatalog = new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            STREAM_NAME_WITH_QUOTES,
            SCHEMA_NAME,
            Field.of("id", JsonSchemaType.NUMBER),
            Field.of("\"test_column\"", JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("id")))));
    testdb.query(ctx -> {
      ctx.fetch("CREATE TABLE \"\"\"test_dq_table\"\"\"(id INTEGER PRIMARY KEY,  \"\"\"test_column\"\"\" varchar);");
      ctx.fetch("INSERT INTO \"\"\"test_dq_table\"\"\" (id, \"\"\"test_column\"\"\") VALUES (1,'test1'),  (2, 'test2');");
      return null;
    });
    final Set<AirbyteMessage> actualMessages =
        MoreIterators.toSet(source().read(
            getConfig(),
            CatalogHelpers.toDefaultConfiguredCatalog(airbyteCatalog),
            null));
    setEmittedAtToNull(actualMessages);
    final var actualRecordMessages = filterRecords(actualMessages);
    assertEquals(DOUBLE_QUOTED_MESSAGES, actualRecordMessages);
    testdb.query(ctx -> ctx.execute("DROP TABLE \"\"\"test_dq_table\"\"\";"));
  }

  @Test
  public void testCanReadUtf8() throws Exception {
    // force the db server to start with sql_ascii encoding to verify the source can read UTF8 even when
    // default settings are in another encoding
    try (final var asciiTestDB = PostgresTestDatabase.in(BaseImage.POSTGRES_16, ContainerModifier.ASCII)
        .with("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));")
        .with("INSERT INTO id_and_name (id, name) VALUES (1,E'\\u2013 someutfstring'),  (2, E'\\u2215');")) {
      final var config = asciiTestDB.testConfigBuilder().withSchemas(SCHEMA_NAME).withoutSsl().build();
      final Set<AirbyteMessage> actualMessages = MoreIterators.toSet(source().read(config, CONFIGURED_CATALOG, null));
      setEmittedAtToNull(actualMessages);
      final var actualRecordMessages = filterRecords(actualMessages);
      assertEquals(UTF8_MESSAGES, actualRecordMessages);
    }
  }

  @Test
  void testUserDoesntHasPrivilegesToSelectTable() throws Exception {
    testdb.query(ctx -> {
      ctx.execute("DROP TABLE id_and_name CASCADE;");
      ctx.execute("DROP TABLE id_and_name2 CASCADE;");
      ctx.execute("DROP TABLE names CASCADE;");
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");
      ctx.fetch("INSERT INTO id_and_name (id, name) VALUES (1,'John'),  (2, 'Alfred'), (3, 'Alex');");
      ctx.fetch("CREATE USER test_user_3 password '132';");
      ctx.fetch("GRANT CONNECT ON DATABASE " + testdb.getDatabaseName() + " TO test_user_3;");
      ctx.fetch("GRANT ALL ON SCHEMA public TO test_user_3");
      ctx.fetch("REVOKE ALL PRIVILEGES ON TABLE public.id_and_name FROM test_user_3");
      return null;
    });
    final JsonNode config = getConfig();
    final DSLContext dslContext = getDslContextWithSpecifiedUser(config, "test_user_3", "132");
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
    final JsonNode anotherUserConfig = getConfig("test_user_3", "132");
    final Set<AirbyteMessage> actualMessages =
        MoreIterators.toSet(source().read(anotherUserConfig, CONFIGURED_CATALOG, null));
    setEmittedAtToNull(actualMessages);
    // expect 6 records and 3 state messages (view does not have its own state message because it goes
    // to non resumable full refresh path).
    assertEquals(9, actualMessages.size());
    final var actualRecordMessages = filterRecords(actualMessages);
    assertEquals(PRIVILEGE_TEST_CASE_EXPECTED_MESSAGES, actualRecordMessages);
  }

  @Test
  void testDiscoverWithPk() throws Exception {
    final AirbyteCatalog actual = source().discover(getConfig());
    actual.getStreams().forEach(actualStream -> {
      final Optional<AirbyteStream> expectedStream =
          CATALOG.getStreams().stream().filter(stream -> stream.getName().equals(actualStream.getName())).findAny();
      assertTrue(expectedStream.isPresent());
      assertEquals(expectedStream.get(), actualStream);
    });
  }

  @Test
  void testDiscoverRecursiveRolePermissions() throws Exception {
    testdb.query(ctx -> {
      ctx.execute("DROP TABLE id_and_name CASCADE;");
      ctx.execute("DROP TABLE id_and_name2 CASCADE;");
      ctx.execute("DROP TABLE names CASCADE;");
      ctx.fetch("CREATE TABLE id_and_name_7(id INTEGER, name VARCHAR(200));");
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));");

      ctx.fetch("CREATE USER test_user_4 password '132';");
      ctx.fetch("GRANT ALL ON SCHEMA public TO test_user_4");

      ctx.fetch("CREATE ROLE airbyte LOGIN password 'airbyte';");
      ctx.fetch("CREATE ROLE read_only LOGIN password 'read_only';");
      ctx.fetch("CREATE ROLE intermediate LOGIN password 'intermediate';");

      ctx.fetch("CREATE ROLE access_nothing LOGIN password 'access_nothing';");

      ctx.fetch("GRANT intermediate TO airbyte;");
      ctx.fetch("GRANT read_only TO intermediate;");

      ctx.fetch("GRANT SELECT ON id_and_name, id_and_name_7 TO read_only;");
      ctx.fetch("GRANT airbyte TO test_user_4;");

      ctx.fetch("CREATE TABLE unseen(id INTEGER, name VARCHAR(200));");
      ctx.fetch("GRANT CONNECT ON DATABASE " + testdb.getDatabaseName() + " TO test_user_4;");
      return null;
    });
    final var config = getConfig();

    final DSLContext dslContext = getDslContextWithSpecifiedUser(config, "test_user_4", "132");
    final Database database = new Database(dslContext);
    database.query(ctx -> {
      ctx.fetch("CREATE TABLE id_and_name_3(id INTEGER, name VARCHAR(200));");
      return null;
    });
    AirbyteCatalog actual = source().discover(getConfig("test_user_4", "132"));
    Set<String> tableNames = actual.getStreams().stream().map(stream -> stream.getName()).collect(Collectors.toSet());
    assertEquals(Sets.newHashSet("id_and_name", "id_and_name_7", "id_and_name_3"), tableNames);

    actual = source().discover(getConfig("access_nothing", "access_nothing"));
    tableNames = actual.getStreams().stream().map(stream -> stream.getName()).collect(Collectors.toSet());
    assertEquals(Sets.newHashSet(), tableNames);
  }

  @Test
  void testDiscoverDifferentGrantAvailability() throws Exception {
    final JsonNode config = getConfig();
    testdb.query(ctx -> {
      ctx.fetch("create table not_granted_table_name_1(column_1 integer);");
      ctx.fetch("create table not_granted_table_name_2(column_1 integer);");
      ctx.fetch("create table not_granted_table_name_3(column_1 integer);");
      ctx.fetch("create table table_granted_by_role(column_1 integer);");
      ctx.fetch("create table test_table_granted_directly(column_1 integer);");
      ctx.fetch("create table table_granted_by_role_with_options(column_1 integer);");
      ctx.fetch("create table test_table_granted_directly_with_options(column_1 integer);");

      ctx.fetch(
          "create materialized view not_granted_mv_name_1 as SELECT not_granted_table_name_1.column_1 FROM not_granted_table_name_1;");
      ctx.fetch(
          "create materialized view not_granted_mv_name_2 as SELECT not_granted_table_name_2.column_1 FROM not_granted_table_name_2;");
      ctx.fetch(
          "create materialized view not_granted_mv_name_3 as SELECT not_granted_table_name_3.column_1 FROM not_granted_table_name_3;");
      ctx.fetch(
          "create materialized view mv_granted_by_role as SELECT table_granted_by_role.column_1 FROM table_granted_by_role;");
      ctx.fetch(
          "create materialized view test_mv_granted_directly as SELECT test_table_granted_directly.column_1 FROM test_table_granted_directly;");
      ctx.fetch(
          "create materialized view mv_granted_by_role_with_options as SELECT table_granted_by_role_with_options.column_1 FROM table_granted_by_role_with_options;");
      ctx.fetch(
          "create materialized view test_mv_granted_directly_with_options as SELECT test_table_granted_directly_with_options.column_1 FROM test_table_granted_directly_with_options;");

      ctx.fetch(
          "create view not_granted_view_name_1(column_1) as SELECT not_granted_table_name_1.column_1 FROM not_granted_table_name_1;");
      ctx.fetch(
          "create view not_granted_view_name_2(column_1) as SELECT not_granted_table_name_2.column_1 FROM not_granted_table_name_2;");
      ctx.fetch(
          "create view not_granted_view_name_3(column_1) as SELECT not_granted_table_name_3.column_1 FROM not_granted_table_name_3;");
      ctx.fetch(
          "create view view_granted_by_role(column_1) as SELECT table_granted_by_role.column_1 FROM table_granted_by_role;");
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
      ctx.fetch("GRANT CONNECT ON DATABASE " + testdb.getDatabaseName() + " TO new_test_user;");
      ctx.fetch("GRANT ALL ON SCHEMA public TO test_user_4");

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

    final AirbyteCatalog actual = source().discover(getConfig("new_test_user", "new_pass"));
    actual.getStreams().stream().forEach(airbyteStream -> {
      assertEquals(2, airbyteStream.getSupportedSyncModes().size());
      assertTrue(airbyteStream.getSupportedSyncModes().contains(SyncMode.FULL_REFRESH));
      assertTrue(airbyteStream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL));
    });
    final Set<String> tableNames =
        actual.getStreams().stream().map(stream -> stream.getName()).collect(Collectors.toSet());
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
  }

  @Test
  void testReadSuccess() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_CATALOG.withStreams(CONFIGURED_CATALOG.getStreams().stream().filter(s -> s.getStream().getName().equals(STREAM_NAME)).collect(
            Collectors.toList()));
    final Set<AirbyteMessage> actualMessages = MoreIterators.toSet(source().read(getConfig(), configuredCatalog, null));
    setEmittedAtToNull(actualMessages);
    final var actualRecordMessages = filterRecords(actualMessages);

    assertEquals(ASCII_MESSAGES, actualRecordMessages);
  }

  @Test
  void testReadIncrementalSuccess() throws Exception {
    // We want to test ordering, so we can delete the NaN entry and add a 3.
    testdb.query(ctx -> {
      ctx.fetch("DELETE FROM id_and_name WHERE id = 'NaN';");
      ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (3, 'gohan', 222.1);");
      return null;
    });

    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_INCR_CATALOG
            .withStreams(CONFIGURED_INCR_CATALOG.getStreams()
                .stream()
                .filter(s -> s.getStream().getName().equals(STREAM_NAME))
                .toList());
    final PostgresSource source = source();
    source.setStateEmissionFrequencyForDebug(1);
    final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(getConfig(), configuredCatalog, null));
    setEmittedAtToNull(actualMessages);

    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessage(actualMessages);

    setEmittedAtToNull(actualMessages);

    final Set<AirbyteMessage> expectedOutput = Sets.newHashSet(
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("1.0"), "name", "goku", "power", null)),
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("2.0"), "name", "vegeta", "power", 9000.1)),
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("3.0"), "name", "vegeta", "power", 222.1)));

    // Assert that the correct number of messages are emitted.
    assertEquals(actualMessages.size(), expectedOutput.size() + 3);
    assertThat(actualMessages.contains(expectedOutput));
    // Assert that the Postgres source is emitting records & state messages in the correct order.
    assertCorrectRecordOrderForIncrementalSync(actualMessages, "id", JsonSchemaPrimitive.NUMBER, configuredCatalog,
        new AirbyteStreamNameNamespacePair("id_and_name", "public"));

    final AirbyteStateMessage lastEmittedState = stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1);
    final JsonNode state = Jsons.jsonNode(List.of(lastEmittedState));

    testdb.query(ctx -> {
      ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (5, 'piccolo', 100.0);");
      return null;
    });
    // Incremental sync should only read one new message (where id = '5.0')
    final Set<AirbyteMessage> nextSyncMessages =
        MoreIterators.toSet(source.read(getConfig(), configuredCatalog, state));
    setEmittedAtToNull(nextSyncMessages);

    // An extra state message is emitted, in addition to the record messages.
    assertEquals(nextSyncMessages.size(), 2);
    assertThat(nextSyncMessages.contains(createRecord(STREAM_NAME, SCHEMA_NAME, map("id", "5.0", "name", "piccolo", "power", 100.0))));
  }

  @Test
  void testReadFullRefreshEmptyTable() throws Exception {
    // Delete all data from id_and_name table.
    testdb.query(ctx -> {
      ctx.fetch("DELETE FROM id_and_name WHERE id = 'NaN';");
      ctx.fetch("DELETE FROM id_and_name WHERE id = '1';");
      ctx.fetch("DELETE FROM id_and_name WHERE id = '2';");
      return null;
    });

    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_CATALOG
            .withStreams(CONFIGURED_CATALOG.getStreams()
                .stream()
                .filter(s -> s.getStream().getName().equals(STREAM_NAME))
                .toList());
    final PostgresSource source = source();
    source.setStateEmissionFrequencyForDebug(1);
    final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(getConfig(), configuredCatalog, null));
    setEmittedAtToNull(actualMessages);

    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessage(actualMessages);

    setEmittedAtToNull(actualMessages);

    // Assert that the correct number of messages are emitted - final state message.
    assertEquals(1, actualMessages.size());
    assertEquals(1, stateAfterFirstBatch.size());

    AirbyteStateMessage stateMessage = stateAfterFirstBatch.get(0);
    assertEquals("ctid", stateMessage.getStream().getStreamState().get("state_type").asText());
    assertEquals("(0,0)", stateMessage.getStream().getStreamState().get("ctid").asText());
  }

  @Test
  void testReadFullRefreshSuccessWithSecondAttempt() throws Exception {
    // We want to test ordering, so we can delete the NaN entry and add a 3.
    testdb.query(ctx -> {
      ctx.fetch("DELETE FROM id_and_name WHERE id = 'NaN';");
      ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (3, 'gohan', 222.1);");
      return null;
    });

    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_CATALOG
            .withStreams(CONFIGURED_CATALOG.getStreams()
                .stream()
                .filter(s -> s.getStream().getName().equals(STREAM_NAME))
                .toList());
    final PostgresSource source = source();
    source.setStateEmissionFrequencyForDebug(1);
    final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(getConfig(), configuredCatalog, null));
    setEmittedAtToNull(actualMessages);

    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessage(actualMessages);

    setEmittedAtToNull(actualMessages);

    final Set<AirbyteMessage> expectedOutput = Sets.newHashSet(
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("1.0"), "name", "goku", "power", null)),
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("2.0"), "name", "vegeta", "power", 9000.1)),
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("3.0"), "name", "vegeta", "power", 222.1)));

    // Assert that the correct number of messages are emitted.
    assertEquals(expectedOutput.size() + 3, actualMessages.size());
    assertThat(actualMessages.contains(expectedOutput));
    // Assert that the Postgres source is emitting records & state messages in the correct order.
    assertCorrectRecordOrderForIncrementalSync(actualMessages, "id", JsonSchemaPrimitive.NUMBER, configuredCatalog,
        new AirbyteStreamNameNamespacePair("id_and_name", "public"));

    final AirbyteStateMessage lastEmittedState = stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1);
    final JsonNode state = Jsons.jsonNode(List.of(lastEmittedState));

    testdb.query(ctx -> {
      ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (5, 'piccolo', 100.0);");
      return null;
    });
    // 2nd sync should reread state checkpoint mark and one new message (where id = '5.0')
    final Set<AirbyteMessage> nextSyncMessages =
        MoreIterators.toSet(source.read(getConfig(), configuredCatalog, state));
    setEmittedAtToNull(nextSyncMessages);

    // A state message is emitted, in addition to the new record messages.
    assertEquals(nextSyncMessages.size(), 2);
    assertThat(nextSyncMessages.contains(createRecord(STREAM_NAME, SCHEMA_NAME, map("id", "5.0", "name", "piccolo", "power", 100.0))));
  }

  @Test
  void testReadFullRefreshSuccessWithSecondAttemptWithVacuum() throws Exception {
    // We want to test ordering, so we can delete the NaN entry and add a 3.
    testdb.query(ctx -> {
      ctx.fetch("DELETE FROM id_and_name WHERE id = 'NaN';");
      ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (3, 'gohan', 222.1);");
      return null;
    });

    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_CATALOG
            .withStreams(CONFIGURED_CATALOG.getStreams()
                .stream()
                .filter(s -> s.getStream().getName().equals(STREAM_NAME))
                .toList());
    final PostgresSource source = source();
    source.setStateEmissionFrequencyForDebug(1);
    final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(getConfig(), configuredCatalog, null));
    setEmittedAtToNull(actualMessages);

    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessage(actualMessages);

    setEmittedAtToNull(actualMessages);

    final Set<AirbyteMessage> expectedOutput = Sets.newHashSet(
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("1.0"), "name", "goku", "power", null)),
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("2.0"), "name", "vegeta", "power", 9000.1)),
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("3.0"), "name", "vegeta", "power", 222.1)));

    // Assert that the correct number of messages are emitted.
    assertEquals(expectedOutput.size() + 3, actualMessages.size());
    assertThat(actualMessages.contains(expectedOutput));
    // Assert that the Postgres source is emitting records & state messages in the correct order.
    assertCorrectRecordOrderForIncrementalSync(actualMessages, "id", JsonSchemaPrimitive.NUMBER, configuredCatalog,
        new AirbyteStreamNameNamespacePair("id_and_name", "public"));

    final AirbyteStateMessage lastEmittedState = stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1);
    final JsonNode state = Jsons.jsonNode(List.of(lastEmittedState));

    testdb.query(ctx -> {
      ctx.fetch("VACUUM full id_and_name");
      ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (5, 'piccolo', 100.0);");
      return null;
    });
    // 2nd sync should reread state checkpoint mark and one new message (where id = '5.0')
    final List<AirbyteMessage> nextSyncMessages =
        MoreIterators.toList(source().read(getConfig(), configuredCatalog, state));
    setEmittedAtToNull(nextSyncMessages);

    // All record messages will be re-read.
    assertEquals(8, nextSyncMessages.size());
    assertThat(nextSyncMessages.contains(createRecord(STREAM_NAME, SCHEMA_NAME, map("id", "5.0", "name", "piccolo", "power", 100.0))));
    assertThat(nextSyncMessages.contains(createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("3.0"), "name", "vegeta", "power", 222.1))));
  }

  @Test
  void testReadIncrementalSuccessWithFullRefresh() throws Exception {
    // We want to test ordering, so we can delete the NaN entry and add a 3.
    testdb.query(ctx -> {
      ctx.fetch("DELETE FROM id_and_name WHERE id = 'NaN';");
      ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (3, 'gohan', 222.1);");
      ctx.fetch("DELETE FROM id_and_name2 WHERE id = 'NaN';");
      ctx.fetch("INSERT INTO id_and_name2 (id, name, power) VALUES (3, 'gohan', 222.1);");
      return null;
    });

    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_INCR_CATALOG
            .withStreams(List.of(CONFIGURED_INCR_CATALOG.getStreams().get(0), CONFIGURED_CATALOG.getStreams().get(1)));
    final PostgresSource source = source();
    source.setStateEmissionFrequencyForDebug(1);
    final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(getConfig(), configuredCatalog, null));
    setEmittedAtToNull(actualMessages);

    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessage(actualMessages);

    setEmittedAtToNull(actualMessages);

    final Set<AirbyteMessage> expectedOutput = Sets.newHashSet(
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("1.0"), "name", "goku", "power", null)),
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("2.0"), "name", "vegeta", "power", 9000.1)),
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("3.0"), "name", "vegeta", "power", 222.1)));

    // Assert that the correct number of messages are emitted. 6 for incremental streams, 6 for full
    // refresh streams.
    assertEquals(actualMessages.size(), 12);
    assertThat(actualMessages.contains(expectedOutput));

    // For per stream, platform will collect states for all streams and compose a new state. Thus, in
    // the test since we want to reset full refresh,
    // we need to get the last state for the "incremental stream", which is not necessarily the last
    // state message of the batch.
    final AirbyteStateMessage lastEmittedState = getLastStateMessageOfStream(stateAfterFirstBatch, STREAM_NAME);

    final JsonNode state = Jsons.jsonNode(List.of(lastEmittedState));

    testdb.query(ctx -> {
      ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (5, 'piccolo', 100.0);");
      return null;
    });
    // Incremental sync should only read one new message (where id = '5.0')
    final List<AirbyteMessage> nextSyncMessages =
        MoreIterators.toList(source().read(getConfig(), configuredCatalog, state));
    setEmittedAtToNull(nextSyncMessages);

    // Incremental stream: An extra state message is emitted, in addition to the record messages.
    // Full refresh stream: expect 4 messages (3 records and 1 state)
    // Thus, we expect 6 messages.
    assertEquals(8, nextSyncMessages.size());
    assertThat(nextSyncMessages.contains(createRecord(STREAM_NAME, SCHEMA_NAME, map("id", "5.0", "name", "piccolo", "power", 100.0))));
  }

  private AirbyteStateMessage getLastStateMessageOfStream(List<AirbyteStateMessage> stateMessages, final String streamName) {
    for (int i = stateMessages.size() - 1; i >= 0; i--) {
      if (stateMessages.get(i).getStream().getStreamDescriptor().getName().equals(streamName)) {
        return stateMessages.get(i);
      }
    }
    throw new RuntimeException("stream not found in state message. stream name: " + streamName);
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
            StateManagerFactory.createStateManager(AirbyteStateType.STREAM, List.of(message.getState()), catalog);
        final Optional<CursorInfo> cursorInfoOptional = stateManager.getCursorInfo(pair);
        final String cursorCandidate = cursorInfoOptional.get().getCursor();
        assertThat(IncrementalUtils.compareCursors(prevStateCursorValue, cursorCandidate, cursorType)).isLessThanOrEqualTo(0);
        prevStateCursorValue = cursorCandidate;
      }
    }
  }

  @Test
  void testIsCdc() {
    final JsonNode config = getConfig();

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
    final ConfiguredAirbyteStream tableWithInvalidCursorType = createTableWithInvalidCursorType(testdb.getDatabase());
    final ConfiguredAirbyteCatalog configuredAirbyteCatalog =
        new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(tableWithInvalidCursorType));

    final Throwable throwable =
        catchThrowable(() -> MoreIterators.toSet(source().read(getConfig(), configuredAirbyteCatalog, null)));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class)
        .hasMessageContaining(
            "The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering with no null values as a cursor. {tableName='public.test_table', cursorColumnName='id', cursorSqlType=OTHER, cause=Unsupported cursor type}");
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
    final JsonNode jdbcConfig = source().toDatabaseConfig(buildConfigEscapingNeeded());
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
    final ConfiguredAirbyteStream table = createTableWithNullValueCursor(testdb.getDatabase());
    final ConfiguredAirbyteCatalog catalog =
        new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(table));

    final Throwable throwable = catchThrowable(() -> MoreIterators.toSet(source().read(getConfig(), catalog, null)));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class).hasMessageContaining(
        "The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering with no null values as a cursor. {tableName='public.test_table_null_cursor', cursorColumnName='id', cursorSqlType=INTEGER, cause=Cursor column contains NULL value}");
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
    final ConfiguredAirbyteStream table = createViewWithNullValueCursor(testdb.getDatabase());
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(table));

    final Throwable throwable = catchThrowable(() -> MoreIterators.toSet(source().read(getConfig(), catalog, null)));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class)
        .hasMessageContaining(
            "The following tables have invalid columns selected as cursor, please select a column with a well-defined ordering with no null values as a cursor. {tableName='public.test_view_null_cursor', cursorColumnName='id', cursorSqlType=INTEGER, cause=Cursor column contains NULL value}");
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

  @Test
  void testParseJdbcParameters() {
    final String jdbcPropertiesString = "foo=bar&options=-c%20search_path=test,public,pg_catalog%20-c%20statement_timeout=90000&baz=quux";
    final Map<String, String> parameters = PostgresSource.parseJdbcParameters(jdbcPropertiesString, "&");
    assertEquals("-c%20search_path=test,public,pg_catalog%20-c%20statement_timeout=90000", parameters.get("options"));
    assertEquals("bar", parameters.get("foo"));
    assertEquals("quux", parameters.get("baz"));
  }

  @Test
  public void testJdbcOptionsParameter() throws Exception {
    // Populate DB.
    final JsonNode dbConfig = getConfig();
    testdb.query(ctx -> {
      ctx.fetch("CREATE TABLE id_and_bytes (id INTEGER, bytes BYTEA);");
      ctx.fetch("INSERT INTO id_and_bytes (id, bytes) VALUES (1, decode('DEADBEEF', 'hex'));");
      return null;
    });

    // Read the table contents using the non-default 'escape' format for bytea values.
    final JsonNode sourceConfig = Jsons.jsonNode(ImmutableMap.builder()
        .putAll(Jsons.flatten(dbConfig))
        .put(JdbcUtils.JDBC_URL_PARAMS_KEY, "options=-c%20statement_timeout=90000%20-c%20bytea_output=escape")
        .build());
    final AirbyteStream airbyteStream = CatalogHelpers.createAirbyteStream(
        "id_and_bytes",
        SCHEMA_NAME,
        Field.of("id", JsonSchemaType.NUMBER),
        Field.of("bytes", JsonSchemaType.STRING))
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
        .withSourceDefinedPrimaryKey(List.of(List.of("id")));
    final AirbyteCatalog airbyteCatalog = new AirbyteCatalog().withStreams(List.of(airbyteStream));
    final Set<AirbyteMessage> actualMessages =
        MoreIterators.toSet(source().read(
            sourceConfig,
            CatalogHelpers.toDefaultConfiguredCatalog(airbyteCatalog),
            null));
    final var actualRecordMessages = filterRecords(actualMessages);

    setEmittedAtToNull(actualRecordMessages);

    // Check that the 'options' JDBC URL parameter was parsed correctly
    // and that the bytea value is not in the default 'hex' format.
    assertEquals(1, actualRecordMessages.size());
    final AirbyteMessage actualMessage = actualRecordMessages.stream().findFirst().get();
    assertTrue(actualMessage.getRecord().getData().has("bytes"));
    assertEquals("\\336\\255\\276\\357", actualMessage.getRecord().getData().get("bytes").asText());
  }

  @Test
  @DisplayName("Make sure initial incremental load is reading records in a certain order")
  void testReadIncrementalRecordOrder() throws Exception {
    // We want to test ordering, so we can delete the NaN entry
    testdb.query(ctx -> {
      ctx.fetch("DELETE FROM id_and_name WHERE id = 'NaN';");
      for (int i = 3; i < 1000; i++) {
        ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (%d, 'gohan%d', 222.1);".formatted(i, i));
      }
      return null;
    });

    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_INCR_CATALOG
            .withStreams(CONFIGURED_INCR_CATALOG.getStreams()
                .stream()
                .filter(s -> s.getStream().getName().equals(STREAM_NAME))
                .toList());
    final PostgresSource source = source();
    source.setStateEmissionFrequencyForDebug(1);
    final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(getConfig(), configuredCatalog, null));
    setEmittedAtToNull(actualMessages);

    // final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessage(actualMessages);

    setEmittedAtToNull(actualMessages);

    final Set<AirbyteMessage> expectedOutput = Sets.newHashSet(
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("1.0"), "name", "goku", "power", null)),
        createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("2.0"), "name", "vegeta", "power", 9000.1)));
    for (int i = 3; i < 1000; i++) {
      expectedOutput.add(
          createRecord(
              STREAM_NAME,
              SCHEMA_NAME,
              map("id", new BigDecimal("%d.0".formatted(i)), "name", "gohan%d".formatted(i), "power", 222.1)));
    }
    assertThat(actualMessages.contains(expectedOutput));
    // Assert that the Postgres source is emitting records & state messages in the correct order.
    assertCorrectRecordOrderForIncrementalSync(actualMessages, "id", JsonSchemaPrimitive.NUMBER, configuredCatalog,
        new AirbyteStreamNameNamespacePair("id_and_name", "public"));
  }

}
