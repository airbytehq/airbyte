/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.jdbc.test;

import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifier;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doCallRealMethod;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.cdk.testutils.TestDatabase;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStateStats;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.math.BigDecimal;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.hamcrest.Matchers;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Tests that should be run on all Sources that extend the AbstractJdbcSource.
 */
@SuppressFBWarnings(
                    value = {"MS_SHOULD_BE_FINAL"},
                    justification = "The static variables are updated in subclasses for convenience, and cannot be final.")
abstract public class JdbcSourceAcceptanceTest<S extends Source, T extends TestDatabase<?, T, ?>> {

  static protected String SCHEMA_NAME = "jdbc_integration_test1";
  static protected String SCHEMA_NAME2 = "jdbc_integration_test2";
  static protected Set<String> TEST_SCHEMAS = Set.of(SCHEMA_NAME, SCHEMA_NAME2);

  static protected String TABLE_NAME = "id_and_name";
  static protected String TABLE_NAME_WITH_SPACES = "id and name";
  static protected String TABLE_NAME_WITHOUT_PK = "id_and_name_without_pk";
  static protected String TABLE_NAME_COMPOSITE_PK = "full_name_composite_pk";
  static protected String TABLE_NAME_WITHOUT_CURSOR_TYPE = "table_without_cursor_type";
  static protected String TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE = "table_with_null_cursor_type";
  // this table is used in testing incremental sync with concurrent insertions
  static protected String TABLE_NAME_AND_TIMESTAMP = "name_and_timestamp";

  static protected String COL_ID = "id";
  static protected String COL_NAME = "name";
  static protected String COL_UPDATED_AT = "updated_at";
  static protected String COL_FIRST_NAME = "first_name";
  static protected String COL_LAST_NAME = "last_name";
  static protected String COL_LAST_NAME_WITH_SPACE = "last name";
  static protected String COL_CURSOR = "cursor_field";
  static protected String COL_TIMESTAMP = "timestamp";
  static protected String COL_TIMESTAMP_TYPE = "TIMESTAMP";
  static protected Number ID_VALUE_1 = 1;
  static protected Number ID_VALUE_2 = 2;
  static protected Number ID_VALUE_3 = 3;
  static protected Number ID_VALUE_4 = 4;
  static protected Number ID_VALUE_5 = 5;

  static protected String DROP_SCHEMA_QUERY = "DROP SCHEMA IF EXISTS %s CASCADE";
  static protected String COLUMN_CLAUSE_WITH_PK = "id INTEGER, name VARCHAR(200) NOT NULL, updated_at DATE NOT NULL";
  static protected String COLUMN_CLAUSE_WITHOUT_PK = "id INTEGER, name VARCHAR(200) NOT NULL, updated_at DATE NOT NULL";
  static protected String COLUMN_CLAUSE_WITH_COMPOSITE_PK =
      "first_name VARCHAR(200) NOT NULL, last_name VARCHAR(200) NOT NULL, updated_at DATE NOT NULL";

  static protected String CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s bit NOT NULL);";
  static protected String INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES(0);";
  static protected String CREATE_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s VARCHAR(20));";
  static protected String INSERT_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES('Hello world :)');";
  static protected String INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY = "INSERT INTO %s (name, timestamp) VALUES ('%s', '%s')";

  protected T testdb;

  protected String streamName() {
    return TABLE_NAME;
  }

  /**
   * A valid configuration to connect to a test database.
   *
   * @return config
   */
  abstract protected JsonNode config();

  /**
   * An instance of the source that should be tests.
   *
   * @return abstract jdbc source
   */
  abstract protected S source();

  /**
   * Creates a TestDatabase instance to be used in {@link #setup()}.
   *
   * @return TestDatabase instance to use for test case.
   */
  abstract protected T createTestDatabase();

  /**
   * These tests write records without specifying a namespace (schema name). They will be written into
   * whatever the default schema is for the database. When they are discovered they will be namespaced
   * by the schema name (e.g. <default-schema-name>.<table_name>). Thus the source needs to tell the
   * tests what that default schema name is. If the database does not support schemas, then database
   * name should used instead.
   *
   * @return name that will be used to namespace the record.
   */
  abstract protected boolean supportsSchemas();

  protected String createTableQuery(final String tableName, final String columnClause, final String primaryKeyClause) {
    return String.format("CREATE TABLE %s(%s %s %s)",
        tableName, columnClause, primaryKeyClause.equals("") ? "" : ",", primaryKeyClause);
  }

  protected String primaryKeyClause(final List<String> columns) {
    if (columns.isEmpty()) {
      return "";
    }

    final StringBuilder clause = new StringBuilder();
    clause.append("PRIMARY KEY (");
    for (int i = 0; i < columns.size(); i++) {
      clause.append(columns.get(i));
      if (i != (columns.size() - 1)) {
        clause.append(",");
      }
    }
    clause.append(")");
    return clause.toString();
  }

  @BeforeEach
  public void setup() throws Exception {
    testdb = createTestDatabase();
    if (supportsSchemas()) {
      createSchemas();
    }
    if (testdb.getDatabaseDriver().equals(DatabaseDriver.ORACLE)) {
      testdb.with("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'");
    }
    testdb
        .with(createTableQuery(getFullyQualifiedTableName(TABLE_NAME), COLUMN_CLAUSE_WITH_PK, primaryKeyClause(Collections.singletonList("id"))))
        .with("INSERT INTO %s(id, name, updated_at) VALUES (1, 'picard', '2004-10-19')", getFullyQualifiedTableName(TABLE_NAME))
        .with("INSERT INTO %s(id, name, updated_at) VALUES (2, 'crusher', '2005-10-19')", getFullyQualifiedTableName(TABLE_NAME))
        .with("INSERT INTO %s(id, name, updated_at) VALUES (3, 'vash', '2006-10-19')", getFullyQualifiedTableName(TABLE_NAME))
        .with(createTableQuery(getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK), COLUMN_CLAUSE_WITHOUT_PK, ""))
        .with("INSERT INTO %s(id, name, updated_at) VALUES (1, 'picard', '2004-10-19')", getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK))
        .with("INSERT INTO %s(id, name, updated_at) VALUES (2, 'crusher', '2005-10-19')", getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK))
        .with("INSERT INTO %s(id, name, updated_at) VALUES (3, 'vash', '2006-10-19')", getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK))
        .with(createTableQuery(getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK), COLUMN_CLAUSE_WITH_COMPOSITE_PK,
            primaryKeyClause(List.of("first_name", "last_name"))))
        .with("INSERT INTO %s(first_name, last_name, updated_at) VALUES ('first', 'picard', '2004-10-19')",
            getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK))
        .with("INSERT INTO %s(first_name, last_name, updated_at) VALUES ('second', 'crusher', '2005-10-19')",
            getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK))
        .with("INSERT INTO %s(first_name, last_name, updated_at) VALUES ('third', 'vash', '2006-10-19')",
            getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK));
  }

  protected void maybeSetShorterConnectionTimeout(final JsonNode config) {
    // Optionally implement this to speed up test cases which will result in a connection timeout.
  }

  @AfterEach
  public void tearDown() {
    testdb.close();
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  @Test
  void testCheckSuccess() throws Exception {
    final AirbyteConnectionStatus actual = source().check(config());
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @Test
  protected void testCheckFailure() throws Exception {
    final var config = config();
    maybeSetShorterConnectionTimeout(config);
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake");
    final AirbyteConnectionStatus actual = source().check(config);
    assertEquals(Status.FAILED, actual.getStatus());
  }

  @Test
  void testDiscover() throws Exception {
    final AirbyteCatalog actual = filterOutOtherSchemas(source().discover(config()));
    final AirbyteCatalog expected = getCatalog(getDefaultNamespace());
    assertEquals(expected.getStreams().size(), actual.getStreams().size());
    actual.getStreams().forEach(actualStream -> {
      final Optional<AirbyteStream> expectedStream =
          expected.getStreams().stream()
              .filter(stream -> stream.getNamespace().equals(actualStream.getNamespace()) && stream.getName().equals(actualStream.getName()))
              .findAny();
      assertTrue(expectedStream.isPresent(), String.format("Unexpected stream %s", actualStream.getName()));
      assertEquals(expectedStream.get(), actualStream);
    });
  }

  @Test
  protected void testDiscoverWithNonCursorFields() throws Exception {
    testdb.with(CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY, getFullyQualifiedTableName(TABLE_NAME_WITHOUT_CURSOR_TYPE), COL_CURSOR)
        .with(INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY, getFullyQualifiedTableName(TABLE_NAME_WITHOUT_CURSOR_TYPE));
    final AirbyteCatalog actual = filterOutOtherSchemas(source().discover(config()));
    final AirbyteStream stream =
        actual.getStreams().stream().filter(s -> s.getName().equalsIgnoreCase(TABLE_NAME_WITHOUT_CURSOR_TYPE)).findFirst().orElse(null);
    assertNotNull(stream);
    assertEquals(TABLE_NAME_WITHOUT_CURSOR_TYPE.toLowerCase(), stream.getName().toLowerCase());
    assertEquals(1, stream.getSupportedSyncModes().size());
    assertEquals(SyncMode.FULL_REFRESH, stream.getSupportedSyncModes().get(0));
  }

  @Test
  protected void testDiscoverWithNullableCursorFields() throws Exception {
    testdb.with(CREATE_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY, getFullyQualifiedTableName(TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE), COL_CURSOR)
        .with(INSERT_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY, getFullyQualifiedTableName(TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE));
    final AirbyteCatalog actual = filterOutOtherSchemas(source().discover(config()));
    final AirbyteStream stream =
        actual.getStreams().stream().filter(s -> s.getName().equalsIgnoreCase(TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE)).findFirst().orElse(null);
    assertNotNull(stream);
    assertEquals(TABLE_NAME_WITH_NULLABLE_CURSOR_TYPE.toLowerCase(), stream.getName().toLowerCase());
    assertEquals(2, stream.getSupportedSyncModes().size());
    assertTrue(stream.getSupportedSyncModes().contains(SyncMode.FULL_REFRESH));
    assertTrue(stream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL));
  }

  protected AirbyteCatalog filterOutOtherSchemas(final AirbyteCatalog catalog) {
    if (supportsSchemas()) {
      final AirbyteCatalog filteredCatalog = Jsons.clone(catalog);
      filteredCatalog.setStreams(filteredCatalog.getStreams()
          .stream()
          .filter(stream -> TEST_SCHEMAS.stream().anyMatch(schemaName -> stream.getNamespace().startsWith(schemaName)))
          .collect(Collectors.toList()));
      return filteredCatalog;
    } else {
      return catalog;
    }

  }

  @Test
  protected void testDiscoverWithMultipleSchemas() throws Exception {
    // clickhouse and mysql do not have a concept of schemas, so this test does not make sense for them.
    switch (testdb.getDatabaseDriver()) {
      case MYSQL, CLICKHOUSE, TERADATA:
        return;
    }

    // add table and data to a separate schema.
    testdb.with("CREATE TABLE %s(id VARCHAR(200) NOT NULL, name VARCHAR(200) NOT NULL)",
        RelationalDbQueryUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME))
        .with("INSERT INTO %s(id, name) VALUES ('1','picard')",
            RelationalDbQueryUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME))
        .with("INSERT INTO %s(id, name) VALUES ('2', 'crusher')",
            RelationalDbQueryUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME))
        .with("INSERT INTO %s(id, name) VALUES ('3', 'vash')",
            RelationalDbQueryUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME));

    final AirbyteCatalog actual = source().discover(config());

    final AirbyteCatalog expected = getCatalog(getDefaultNamespace());
    final List<AirbyteStream> catalogStreams = new ArrayList<>();
    catalogStreams.addAll(expected.getStreams());
    catalogStreams.add(CatalogHelpers
        .createAirbyteStream(TABLE_NAME,
            SCHEMA_NAME2,
            Field.of(COL_ID, JsonSchemaType.STRING),
            Field.of(COL_NAME, JsonSchemaType.STRING))
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)));
    expected.setStreams(catalogStreams);
    // sort streams by name so that we are comparing lists with the same order.
    final Comparator<AirbyteStream> schemaTableCompare = Comparator.comparing(stream -> stream.getNamespace() + "." + stream.getName());
    expected.getStreams().sort(schemaTableCompare);
    actual.getStreams().sort(schemaTableCompare);
    assertEquals(expected, filterOutOtherSchemas(actual));
  }

  @Test
  void testReadSuccess() throws Exception {
    final List<AirbyteMessage> actualMessages =
        MoreIterators.toList(
            source().read(config(), getConfiguredCatalogWithOneStream(getDefaultNamespace()), null));

    setEmittedAtToNull(actualMessages);
    final List<AirbyteMessage> expectedMessages = getTestMessages();
    assertThat(expectedMessages, Matchers.containsInAnyOrder(actualMessages.toArray()));
    assertThat(actualMessages, Matchers.containsInAnyOrder(expectedMessages.toArray()));
  }

  @Test
  protected void testReadOneColumn() throws Exception {
    final ConfiguredAirbyteCatalog catalog = CatalogHelpers
        .createConfiguredAirbyteCatalog(streamName(), getDefaultNamespace(), Field.of(COL_ID, JsonSchemaType.NUMBER));
    final List<AirbyteMessage> actualMessages = MoreIterators
        .toList(source().read(config(), catalog, null));

    setEmittedAtToNull(actualMessages);

    final List<AirbyteMessage> expectedMessages = getAirbyteMessagesReadOneColumn();
    assertEquals(expectedMessages.size(), actualMessages.size());
    assertTrue(expectedMessages.containsAll(actualMessages));
    assertTrue(actualMessages.containsAll(expectedMessages));
  }

  protected List<AirbyteMessage> getAirbyteMessagesReadOneColumn() {
    final List<AirbyteMessage> expectedMessages = getTestMessages().stream()
        .map(Jsons::clone)
        .peek(m -> {
          ((ObjectNode) m.getRecord().getData()).remove(COL_NAME);
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              convertIdBasedOnDatabase(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());
    return expectedMessages;
  }

  @Test
  protected void testReadMultipleTables() throws Exception {
    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalogWithOneStream(
        getDefaultNamespace());
    final List<AirbyteMessage> expectedMessages = new ArrayList<>(getTestMessages());

    for (int i = 2; i < 10; i++) {
      final String streamName2 = streamName() + i;
      final String tableName = getFullyQualifiedTableName(TABLE_NAME + i);
      testdb.with(createTableQuery(tableName, "id INTEGER, name VARCHAR(200)", ""))
          .with("INSERT INTO %s(id, name) VALUES (1,'picard')", tableName)
          .with("INSERT INTO %s(id, name) VALUES (2, 'crusher')", tableName)
          .with("INSERT INTO %s(id, name) VALUES (3, 'vash')", tableName);
      catalog.getStreams().add(CatalogHelpers.createConfiguredAirbyteStream(
          streamName2,
          getDefaultNamespace(),
          Field.of(COL_ID, JsonSchemaType.NUMBER),
          Field.of(COL_NAME, JsonSchemaType.STRING)));

      expectedMessages.addAll(getAirbyteMessagesSecondSync(streamName2));
    }

    final List<AirbyteMessage> actualMessages = MoreIterators
        .toList(source().read(config(), catalog, null));

    setEmittedAtToNull(actualMessages);

    assertEquals(expectedMessages.size(), actualMessages.size());
    assertTrue(expectedMessages.containsAll(actualMessages));
    assertTrue(actualMessages.containsAll(expectedMessages));
  }

  protected List<AirbyteMessage> getAirbyteMessagesSecondSync(final String streamName) {
    return getTestMessages()
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamName);
          m.getRecord().setNamespace(getDefaultNamespace());
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              convertIdBasedOnDatabase(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());

  }

  @Test
  protected void testTablesWithQuoting() throws Exception {
    final ConfiguredAirbyteStream streamForTableWithSpaces = createTableWithSpaces();

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(
            getConfiguredCatalogWithOneStream(getDefaultNamespace()).getStreams().get(0),
            streamForTableWithSpaces));
    final List<AirbyteMessage> actualMessages = MoreIterators
        .toList(source().read(config(), catalog, null));

    setEmittedAtToNull(actualMessages);

    final List<AirbyteMessage> expectedMessages = new ArrayList<>(getTestMessages());
    expectedMessages.addAll(getAirbyteMessagesForTablesWithQuoting(streamForTableWithSpaces));

    assertEquals(expectedMessages.size(), actualMessages.size());
    assertTrue(expectedMessages.containsAll(actualMessages));
    assertTrue(actualMessages.containsAll(expectedMessages));
  }

  protected List<AirbyteMessage> getAirbyteMessagesForTablesWithQuoting(final ConfiguredAirbyteStream streamForTableWithSpaces) {
    return getTestMessages()
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamForTableWithSpaces.getStream().getName());
          ((ObjectNode) m.getRecord().getData()).set(COL_LAST_NAME_WITH_SPACE,
              ((ObjectNode) m.getRecord().getData()).remove(COL_NAME));
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              convertIdBasedOnDatabase(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testReadFailure() {
    final ConfiguredAirbyteStream spiedAbStream = spy(
        getConfiguredCatalogWithOneStream(getDefaultNamespace()).getStreams().get(0));
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(spiedAbStream));
    doCallRealMethod().doThrow(new RuntimeException()).when(spiedAbStream).getStream();

    assertThrows(RuntimeException.class, () -> source().read(config(), catalog, null));
  }

  @Test
  void testIncrementalNoPreviousState() throws Exception {
    incrementalCursorCheck(
        COL_ID,
        null,
        "3",
        getTestMessages());
  }

  @Test
  void testIncrementalIntCheckCursor() throws Exception {
    incrementalCursorCheck(
        COL_ID,
        "2",
        "3",
        List.of(getTestMessages().get(2)));
  }

  @Test
  void testIncrementalStringCheckCursor() throws Exception {
    incrementalCursorCheck(
        COL_NAME,
        "patent",
        "vash",
        List.of(getTestMessages().get(0), getTestMessages().get(2)));
  }

  @Test
  void testIncrementalStringCheckCursorSpaceInColumnName() throws Exception {
    final ConfiguredAirbyteStream streamWithSpaces = createTableWithSpaces();

    final List<AirbyteMessage> expectedRecordMessages = getAirbyteMessagesCheckCursorSpaceInColumnName(streamWithSpaces);
    incrementalCursorCheck(
        COL_LAST_NAME_WITH_SPACE,
        COL_LAST_NAME_WITH_SPACE,
        "patent",
        "vash",
        expectedRecordMessages,
        streamWithSpaces);
  }

  protected List<AirbyteMessage> getAirbyteMessagesCheckCursorSpaceInColumnName(final ConfiguredAirbyteStream streamWithSpaces) {
    final AirbyteMessage firstMessage = getTestMessages().get(0);
    firstMessage.getRecord().setStream(streamWithSpaces.getStream().getName());
    ((ObjectNode) firstMessage.getRecord().getData()).remove(COL_UPDATED_AT);
    ((ObjectNode) firstMessage.getRecord().getData()).set(COL_LAST_NAME_WITH_SPACE,
        ((ObjectNode) firstMessage.getRecord().getData()).remove(COL_NAME));

    final AirbyteMessage secondMessage = getTestMessages().get(2);
    secondMessage.getRecord().setStream(streamWithSpaces.getStream().getName());
    ((ObjectNode) secondMessage.getRecord().getData()).remove(COL_UPDATED_AT);
    ((ObjectNode) secondMessage.getRecord().getData()).set(COL_LAST_NAME_WITH_SPACE,
        ((ObjectNode) secondMessage.getRecord().getData()).remove(COL_NAME));

    return List.of(firstMessage, secondMessage);
  }

  @Test
  void testIncrementalDateCheckCursor() throws Exception {
    incrementalDateCheck();
  }

  protected void incrementalDateCheck() throws Exception {
    incrementalCursorCheck(
        COL_UPDATED_AT,
        "2005-10-18",
        "2006-10-19",
        List.of(getTestMessages().get(1), getTestMessages().get(2)));
  }

  @Test
  void testIncrementalCursorChanges() throws Exception {
    incrementalCursorCheck(
        COL_ID,
        COL_NAME,
        // cheesing this value a little bit. in the correct implementation this initial cursor value should
        // be ignored because the cursor field changed. setting it to a value that if used, will cause
        // records to (incorrectly) be filtered out.
        "data",
        "vash",
        getTestMessages());
  }

  @Test
  protected void testReadOneTableIncrementallyTwice() throws Exception {
    final var config = config();
    final String namespace = getDefaultNamespace();
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalogWithOneStream(namespace);
    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(List.of(COL_ID));
      airbyteStream.setDestinationSyncMode(DestinationSyncMode.APPEND);
    });

    final List<AirbyteMessage> actualMessagesFirstSync = MoreIterators
        .toList(source().read(config, configuredCatalog, createEmptyState(streamName(), namespace)));

    final Optional<AirbyteMessage> stateAfterFirstSyncOptional = actualMessagesFirstSync.stream()
        .filter(r -> r.getType() == Type.STATE).findFirst();
    assertTrue(stateAfterFirstSyncOptional.isPresent());

    executeStatementReadIncrementallyTwice();

    final List<AirbyteMessage> actualMessagesSecondSync = MoreIterators
        .toList(source().read(config, configuredCatalog, extractState(stateAfterFirstSyncOptional.get())));

    assertEquals(2,
        (int) actualMessagesSecondSync.stream().filter(r -> r.getType() == Type.RECORD).count());
    final List<AirbyteMessage> expectedMessages = getExpectedAirbyteMessagesSecondSync(namespace);

    setEmittedAtToNull(actualMessagesSecondSync);

    assertEquals(expectedMessages.size(), actualMessagesSecondSync.size());
    assertTrue(expectedMessages.containsAll(actualMessagesSecondSync));
    assertTrue(actualMessagesSecondSync.containsAll(expectedMessages));
  }

  protected void executeStatementReadIncrementallyTwice() {
    testdb
        .with("INSERT INTO %s (id, name, updated_at) VALUES (4, 'riker', '2006-10-19')", getFullyQualifiedTableName(TABLE_NAME))
        .with("INSERT INTO %s (id, name, updated_at) VALUES (5, 'data', '2006-10-19')", getFullyQualifiedTableName(TABLE_NAME));
  }

  protected List<AirbyteMessage> getExpectedAirbyteMessagesSecondSync(final String namespace) {
    final List<AirbyteMessage> expectedMessages = new ArrayList<>();
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName()).withNamespace(namespace)
            .withData(Jsons.jsonNode(Map
                .of(COL_ID, ID_VALUE_4,
                    COL_NAME, "riker",
                    COL_UPDATED_AT, "2006-10-19")))));
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName()).withNamespace(namespace)
            .withData(Jsons.jsonNode(Map
                .of(COL_ID, ID_VALUE_5,
                    COL_NAME, "data",
                    COL_UPDATED_AT, "2006-10-19")))));
    final DbStreamState state = new DbStreamState()
        .withStreamName(streamName())
        .withStreamNamespace(namespace)
        .withCursorField(List.of(COL_ID))
        .withCursor("5")
        .withCursorRecordCount(1L);
    expectedMessages.addAll(createExpectedTestMessages(List.of(state), 2L));
    return expectedMessages;
  }

  @Test
  protected void testReadMultipleTablesIncrementally() throws Exception {
    final String tableName2 = TABLE_NAME + 2;
    final String streamName2 = streamName() + 2;
    final String fqTableName2 = getFullyQualifiedTableName(tableName2);
    testdb.with(createTableQuery(fqTableName2, "id INTEGER, name VARCHAR(200)", ""))
        .with("INSERT INTO %s(id, name) VALUES (1,'picard')", fqTableName2)
        .with("INSERT INTO %s(id, name) VALUES (2, 'crusher')", fqTableName2)
        .with("INSERT INTO %s(id, name) VALUES (3, 'vash')", fqTableName2);

    final String namespace = getDefaultNamespace();
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalogWithOneStream(
        namespace);
    configuredCatalog.getStreams().add(CatalogHelpers.createConfiguredAirbyteStream(
        streamName2,
        namespace,
        Field.of(COL_ID, JsonSchemaType.NUMBER),
        Field.of(COL_NAME, JsonSchemaType.STRING)));
    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(List.of(COL_ID));
      airbyteStream.setDestinationSyncMode(DestinationSyncMode.APPEND);
    });

    final List<AirbyteMessage> actualMessagesFirstSync = MoreIterators
        .toList(source().read(config(), configuredCatalog, createEmptyState(streamName(), namespace)));

    // get last state message.
    final Optional<AirbyteMessage> stateAfterFirstSyncOptional = actualMessagesFirstSync.stream()
        .filter(r -> r.getType() == Type.STATE)
        .reduce((first, second) -> second);
    assertTrue(stateAfterFirstSyncOptional.isPresent());

    // we know the second streams messages are the same as the first minus the updated at column. so we
    // cheat and generate the expected messages off of the first expected messages.
    final List<AirbyteMessage> secondStreamExpectedMessages = getAirbyteMessagesSecondStreamWithNamespace(streamName2);

    // Represents the state after the first stream has been updated
    final List<DbStreamState> expectedStateStreams1 = List.of(
        new DbStreamState()
            .withStreamName(streamName())
            .withStreamNamespace(namespace)
            .withCursorField(List.of(COL_ID))
            .withCursor("3")
            .withCursorRecordCount(1L),
        new DbStreamState()
            .withStreamName(streamName2)
            .withStreamNamespace(namespace)
            .withCursorField(List.of(COL_ID)));

    // Represents the state after both streams have been updated
    final List<DbStreamState> expectedStateStreams2 = List.of(
        new DbStreamState()
            .withStreamName(streamName())
            .withStreamNamespace(namespace)
            .withCursorField(List.of(COL_ID))
            .withCursor("3")
            .withCursorRecordCount(1L),
        new DbStreamState()
            .withStreamName(streamName2)
            .withStreamNamespace(namespace)
            .withCursorField(List.of(COL_ID))
            .withCursor("3")
            .withCursorRecordCount(1L));

    final List<AirbyteMessage> expectedMessagesFirstSync = new ArrayList<>(getTestMessages());
    expectedMessagesFirstSync.add(createStateMessage(expectedStateStreams1.get(0), expectedStateStreams1, 3L));
    expectedMessagesFirstSync.addAll(secondStreamExpectedMessages);
    expectedMessagesFirstSync.add(createStateMessage(expectedStateStreams2.get(1), expectedStateStreams2, 3L));

    setEmittedAtToNull(actualMessagesFirstSync);

    assertEquals(expectedMessagesFirstSync.size(), actualMessagesFirstSync.size());
    assertTrue(expectedMessagesFirstSync.containsAll(actualMessagesFirstSync));
    assertTrue(actualMessagesFirstSync.containsAll(expectedMessagesFirstSync));
  }

  protected List<AirbyteMessage> getAirbyteMessagesSecondStreamWithNamespace(final String streamName2) {
    return getTestMessages()
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamName2);
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              convertIdBasedOnDatabase(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());
  }

  // when initial and final cursor fields are the same.
  protected void incrementalCursorCheck(
                                        final String cursorField,
                                        final String initialCursorValue,
                                        final String endCursorValue,
                                        final List<AirbyteMessage> expectedRecordMessages)
      throws Exception {
    incrementalCursorCheck(cursorField, cursorField, initialCursorValue, endCursorValue,
        expectedRecordMessages);
  }

  // See https://github.com/airbytehq/airbyte/issues/14732 for rationale and details.
  @Test
  public void testIncrementalWithConcurrentInsertion() throws Exception {
    final String namespace = getDefaultNamespace();
    final String fullyQualifiedTableName = getFullyQualifiedTableName(TABLE_NAME_AND_TIMESTAMP);
    final String columnDefinition = String.format("name VARCHAR(200) NOT NULL, %s %s NOT NULL", COL_TIMESTAMP, COL_TIMESTAMP_TYPE);

    // 1st sync
    testdb.with(createTableQuery(fullyQualifiedTableName, columnDefinition, ""))
        .with(INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY, fullyQualifiedTableName, "a", "2021-01-01 00:00:00")
        .with(INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY, fullyQualifiedTableName, "b", "2021-01-01 00:00:00");

    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(
        new AirbyteCatalog().withStreams(List.of(
            CatalogHelpers.createAirbyteStream(
                TABLE_NAME_AND_TIMESTAMP,
                namespace,
                Field.of(COL_NAME, JsonSchemaType.STRING),
                Field.of(COL_TIMESTAMP, JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE)))));

    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(List.of(COL_TIMESTAMP));
      airbyteStream.setDestinationSyncMode(DestinationSyncMode.APPEND);
    });

    final List<AirbyteMessage> firstSyncActualMessages = MoreIterators.toList(
        source().read(config(), configuredCatalog, createEmptyState(TABLE_NAME_AND_TIMESTAMP, namespace)));

    // cursor after 1st sync: 2021-01-01 00:00:00, count 2
    final Optional<AirbyteMessage> firstSyncStateOptional = firstSyncActualMessages.stream().filter(r -> r.getType() == Type.STATE).findFirst();
    assertTrue(firstSyncStateOptional.isPresent());
    final JsonNode firstSyncState = getStateData(firstSyncStateOptional.get(), TABLE_NAME_AND_TIMESTAMP);
    assertEquals(firstSyncState.get("cursor_field").elements().next().asText(), COL_TIMESTAMP);
    assertTrue(firstSyncState.get("cursor").asText().contains("2021-01-01"));
    assertTrue(firstSyncState.get("cursor").asText().contains("00:00:00"));
    assertEquals(2L, firstSyncState.get("cursor_record_count").asLong());

    final List<String> firstSyncNames = firstSyncActualMessages.stream()
        .filter(r -> r.getType() == Type.RECORD)
        .map(r -> r.getRecord().getData().get(COL_NAME).asText())
        .toList();
    // some databases don't make insertion order guarantee when equal ordering value
    if (testdb.getDatabaseDriver().equals(DatabaseDriver.TERADATA) || testdb.getDatabaseDriver().equals(DatabaseDriver.ORACLE)) {
      assertThat(List.of("a", "b"), Matchers.containsInAnyOrder(firstSyncNames.toArray()));
    } else {
      assertEquals(List.of("a", "b"), firstSyncNames);
    }

    // 2nd sync
    testdb.with(INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY, fullyQualifiedTableName, "c", "2021-01-02 00:00:00");

    final List<AirbyteMessage> secondSyncActualMessages = MoreIterators.toList(
        source().read(config(), configuredCatalog, createState(TABLE_NAME_AND_TIMESTAMP, namespace, firstSyncState)));

    // cursor after 2nd sync: 2021-01-02 00:00:00, count 1
    final Optional<AirbyteMessage> secondSyncStateOptional = secondSyncActualMessages.stream().filter(r -> r.getType() == Type.STATE).findFirst();
    assertTrue(secondSyncStateOptional.isPresent());
    final JsonNode secondSyncState = getStateData(secondSyncStateOptional.get(), TABLE_NAME_AND_TIMESTAMP);
    assertEquals(secondSyncState.get("cursor_field").elements().next().asText(), COL_TIMESTAMP);
    assertTrue(secondSyncState.get("cursor").asText().contains("2021-01-02"));
    assertTrue(secondSyncState.get("cursor").asText().contains("00:00:00"));
    assertEquals(1L, secondSyncState.get("cursor_record_count").asLong());

    final List<String> secondSyncNames = secondSyncActualMessages.stream()
        .filter(r -> r.getType() == Type.RECORD)
        .map(r -> r.getRecord().getData().get(COL_NAME).asText())
        .toList();
    assertEquals(List.of("c"), secondSyncNames);

    // 3rd sync has records with duplicated cursors
    testdb.with(INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY, fullyQualifiedTableName, "d", "2021-01-02 00:00:00")
        .with(INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY, fullyQualifiedTableName, "e", "2021-01-02 00:00:00")
        .with(INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY, fullyQualifiedTableName, "f", "2021-01-03 00:00:00");

    final List<AirbyteMessage> thirdSyncActualMessages = MoreIterators.toList(
        source().read(config(), configuredCatalog, createState(TABLE_NAME_AND_TIMESTAMP, namespace, secondSyncState)));

    // Cursor after 3rd sync is: 2021-01-03 00:00:00, count 1.
    final Optional<AirbyteMessage> thirdSyncStateOptional = thirdSyncActualMessages.stream().filter(r -> r.getType() == Type.STATE).findFirst();
    assertTrue(thirdSyncStateOptional.isPresent());
    final JsonNode thirdSyncState = getStateData(thirdSyncStateOptional.get(), TABLE_NAME_AND_TIMESTAMP);
    assertEquals(thirdSyncState.get("cursor_field").elements().next().asText(), COL_TIMESTAMP);
    assertTrue(thirdSyncState.get("cursor").asText().contains("2021-01-03"));
    assertTrue(thirdSyncState.get("cursor").asText().contains("00:00:00"));
    assertEquals(1L, thirdSyncState.get("cursor_record_count").asLong());

    // The c, d, e, f are duplicated records from this sync, because the cursor
    // record count in the database is different from that in the state.
    final List<String> thirdSyncExpectedNames = thirdSyncActualMessages.stream()
        .filter(r -> r.getType() == Type.RECORD)
        .map(r -> r.getRecord().getData().get(COL_NAME).asText())
        .toList();

    // teradata doesn't make insertion order guarantee when equal ordering value
    if (testdb.getDatabaseDriver().equals(DatabaseDriver.TERADATA)) {
      assertThat(List.of("c", "d", "e", "f"), Matchers.containsInAnyOrder(thirdSyncExpectedNames.toArray()));
    } else {
      assertEquals(List.of("c", "d", "e", "f"), thirdSyncExpectedNames);
    }
  }

  protected JsonNode getStateData(final AirbyteMessage airbyteMessage, final String streamName) {
    for (final JsonNode stream : airbyteMessage.getState().getData().get("streams")) {
      if (stream.get("stream_name").asText().equals(streamName)) {
        return stream;
      }
    }
    throw new IllegalArgumentException("Stream not found in state message: " + streamName);
  }

  private void incrementalCursorCheck(
                                      final String initialCursorField,
                                      final String cursorField,
                                      final String initialCursorValue,
                                      final String endCursorValue,
                                      final List<AirbyteMessage> expectedRecordMessages)
      throws Exception {
    incrementalCursorCheck(initialCursorField, cursorField, initialCursorValue, endCursorValue,
        expectedRecordMessages,
        getConfiguredCatalogWithOneStream(getDefaultNamespace()).getStreams().get(0));
  }

  protected void incrementalCursorCheck(
                                        final String initialCursorField,
                                        final String cursorField,
                                        final String initialCursorValue,
                                        final String endCursorValue,
                                        final List<AirbyteMessage> expectedRecordMessages,
                                        final ConfiguredAirbyteStream airbyteStream)
      throws Exception {
    airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
    airbyteStream.setCursorField(List.of(cursorField));
    airbyteStream.setDestinationSyncMode(DestinationSyncMode.APPEND);

    final ConfiguredAirbyteCatalog configuredCatalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(airbyteStream));

    final DbStreamState dbStreamState = buildStreamState(airbyteStream, initialCursorField, initialCursorValue);

    final List<AirbyteMessage> actualMessages = MoreIterators
        .toList(source().read(config(), configuredCatalog, Jsons.jsonNode(createState(List.of(dbStreamState)))));

    setEmittedAtToNull(actualMessages);

    final List<DbStreamState> expectedStreams = List.of(buildStreamState(airbyteStream, cursorField, endCursorValue));

    final List<AirbyteMessage> expectedMessages = new ArrayList<>(expectedRecordMessages);
    expectedMessages.addAll(createExpectedTestMessages(expectedStreams, expectedRecordMessages.size()));

    assertEquals(expectedMessages.size(), actualMessages.size());
    assertTrue(expectedMessages.containsAll(actualMessages));
    assertTrue(actualMessages.containsAll(expectedMessages));
  }

  protected DbStreamState buildStreamState(final ConfiguredAirbyteStream configuredAirbyteStream,
                                           final String cursorField,
                                           final String cursorValue) {
    return new DbStreamState()
        .withStreamName(configuredAirbyteStream.getStream().getName())
        .withStreamNamespace(configuredAirbyteStream.getStream().getNamespace())
        .withCursorField(List.of(cursorField))
        .withCursor(cursorValue)
        .withCursorRecordCount(1L);
  }

  // get catalog and perform a defensive copy.
  protected ConfiguredAirbyteCatalog getConfiguredCatalogWithOneStream(final String defaultNamespace) {
    final ConfiguredAirbyteCatalog catalog = CatalogHelpers.toDefaultConfiguredCatalog(getCatalog(defaultNamespace));
    // Filter to only keep the main stream name as configured stream
    catalog.withStreams(
        catalog.getStreams().stream().filter(s -> s.getStream().getName().equals(streamName()))
            .collect(Collectors.toList()));
    return catalog;
  }

  protected AirbyteCatalog getCatalog(final String defaultNamespace) {
    return new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_WITHOUT_PK,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(Collections.emptyList()),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_COMPOSITE_PK,
            defaultNamespace,
            Field.of(COL_FIRST_NAME, JsonSchemaType.STRING),
            Field.of(COL_LAST_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(
                List.of(List.of(COL_FIRST_NAME), List.of(COL_LAST_NAME)))));
  }

  protected List<AirbyteMessage> getTestMessages() {
    return List.of(
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName()).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_1,
                        COL_NAME, "picard",
                        COL_UPDATED_AT, "2004-10-19")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName()).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_2,
                        COL_NAME, "crusher",
                        COL_UPDATED_AT,
                        "2005-10-19")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName()).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_3,
                        COL_NAME, "vash",
                        COL_UPDATED_AT, "2006-10-19")))));
  }

  protected List<AirbyteMessage> createExpectedTestMessages(final List<DbStreamState> states, final long numRecords) {
    return states.stream()
        .map(s -> new AirbyteMessage().withType(Type.STATE)
            .withState(
                new AirbyteStateMessage().withType(AirbyteStateType.STREAM)
                    .withStream(new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withNamespace(s.getStreamNamespace()).withName(s.getStreamName()))
                        .withStreamState(Jsons.jsonNode(s)))
                    .withData(Jsons.jsonNode(new DbState().withCdc(false).withStreams(states)))
                    .withSourceStats(new AirbyteStateStats().withRecordCount((double) numRecords))))
        .collect(
            Collectors.toList());
  }

  protected List<AirbyteStateMessage> createState(final List<DbStreamState> states) {
    return states.stream()
        .map(s -> new AirbyteStateMessage().withType(AirbyteStateType.STREAM)
            .withStream(new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withNamespace(s.getStreamNamespace()).withName(s.getStreamName()))
                .withStreamState(Jsons.jsonNode(s))))
        .collect(
            Collectors.toList());
  }

  protected ConfiguredAirbyteStream createTableWithSpaces() throws SQLException {
    final String tableNameWithSpaces = TABLE_NAME_WITH_SPACES + "2";
    final String streamName2 = tableNameWithSpaces;

    try (final var connection = testdb.getDataSource().getConnection()) {
      final String identifierQuoteString = connection.getMetaData().getIdentifierQuoteString();
      connection.createStatement()
          .execute(
              createTableQuery(getFullyQualifiedTableName(
                  enquoteIdentifier(tableNameWithSpaces, identifierQuoteString)),
                  "id INTEGER, " + enquoteIdentifier(COL_LAST_NAME_WITH_SPACE, identifierQuoteString)
                      + " VARCHAR(200)",
                  ""));
      connection.createStatement()
          .execute(String.format("INSERT INTO %s(id, %s) VALUES (1,'picard')",
              getFullyQualifiedTableName(
                  enquoteIdentifier(tableNameWithSpaces, identifierQuoteString)),
              enquoteIdentifier(COL_LAST_NAME_WITH_SPACE, identifierQuoteString)));
      connection.createStatement()
          .execute(String.format("INSERT INTO %s(id, %s) VALUES (2, 'crusher')",
              getFullyQualifiedTableName(
                  enquoteIdentifier(tableNameWithSpaces, identifierQuoteString)),
              enquoteIdentifier(COL_LAST_NAME_WITH_SPACE, identifierQuoteString)));
      connection.createStatement()
          .execute(String.format("INSERT INTO %s(id, %s) VALUES (3, 'vash')",
              getFullyQualifiedTableName(
                  enquoteIdentifier(tableNameWithSpaces, identifierQuoteString)),
              enquoteIdentifier(COL_LAST_NAME_WITH_SPACE, identifierQuoteString)));
    }

    return CatalogHelpers.createConfiguredAirbyteStream(
        streamName2,
        getDefaultNamespace(),
        Field.of(COL_ID, JsonSchemaType.NUMBER),
        Field.of(COL_LAST_NAME_WITH_SPACE, JsonSchemaType.STRING));
  }

  public String getFullyQualifiedTableName(final String tableName) {
    return RelationalDbQueryUtils.getFullyQualifiedTableName(getDefaultSchemaName(), tableName);
  }

  protected void createSchemas() {
    if (supportsSchemas()) {
      for (final String schemaName : TEST_SCHEMAS) {
        testdb.with("CREATE SCHEMA %s;", schemaName);
      }
    }
  }

  private JsonNode convertIdBasedOnDatabase(final int idValue) {
    return switch (testdb.getDatabaseDriver()) {
      case ORACLE, SNOWFLAKE -> Jsons.jsonNode(BigDecimal.valueOf(idValue));
      default -> Jsons.jsonNode(idValue);
    };
  }

  private String getDefaultSchemaName() {
    return supportsSchemas() ? SCHEMA_NAME : null;
  }

  protected String getDefaultNamespace() {
    return switch (testdb.getDatabaseDriver()) {
      // mysql does not support schemas, it namespaces using database names instead.
      case MYSQL, CLICKHOUSE, TERADATA -> testdb.getDatabaseName();
      default -> SCHEMA_NAME;
    };
  }

  protected static void setEmittedAtToNull(final Iterable<AirbyteMessage> messages) {
    for (final AirbyteMessage actualMessage : messages) {
      if (actualMessage.getRecord() != null) {
        actualMessage.getRecord().setEmittedAt(null);
      }
    }
  }

  /**
   * Creates empty state with the provided stream name and namespace.
   *
   * @param streamName The stream name.
   * @param streamNamespace The stream namespace.
   * @return {@link JsonNode} representation of the generated empty state.
   */
  protected JsonNode createEmptyState(final String streamName, final String streamNamespace) {
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName(streamName).withNamespace(streamNamespace)));
    return Jsons.jsonNode(List.of(airbyteStateMessage));

  }

  protected JsonNode createState(final String streamName, final String streamNamespace, final JsonNode stateData) {
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(streamName).withNamespace(streamNamespace))
                .withStreamState(stateData));
    return Jsons.jsonNode(List.of(airbyteStateMessage));
  }

  protected JsonNode extractState(final AirbyteMessage airbyteMessage) {
    return Jsons.jsonNode(List.of(airbyteMessage.getState()));
  }

  protected AirbyteMessage createStateMessage(final DbStreamState dbStreamState, final List<DbStreamState> legacyStates, final long recordCount) {
    return new AirbyteMessage().withType(Type.STATE)
        .withState(
            new AirbyteStateMessage().withType(AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState()
                    .withStreamDescriptor(new StreamDescriptor().withNamespace(dbStreamState.getStreamNamespace())
                        .withName(dbStreamState.getStreamName()))
                    .withStreamState(Jsons.jsonNode(dbStreamState)))
                .withData(Jsons.jsonNode(new DbState().withCdc(false).withStreams(legacyStates)))
                .withSourceStats(new AirbyteStateStats().withRecordCount((double) recordCount)));
  }

  protected List<String> extractSpecificFieldFromCombinedMessages(final List<AirbyteMessage> messages,
                                                                  final String streamName,
                                                                  final String field) {
    return extractStateMessage(messages).stream()
        .filter(s -> s.getStream().getStreamDescriptor().getName().equals(streamName))
        .map(s -> s.getStream().getStreamState().get(field) != null ? s.getStream().getStreamState().get(field).asText() : "").toList();
  }

  protected List<AirbyteMessage> filterRecords(final List<AirbyteMessage> messages) {
    return messages.stream().filter(r -> r.getType() == Type.RECORD)
        .collect(Collectors.toList());
  }

  protected List<AirbyteStateMessage> extractStateMessage(final List<AirbyteMessage> messages) {
    return messages.stream().filter(r -> r.getType() == Type.STATE).map(AirbyteMessage::getState)
        .collect(Collectors.toList());
  }

  protected List<AirbyteStateMessage> extractStateMessage(final List<AirbyteMessage> messages, final String streamName) {
    return messages.stream().filter(r -> r.getType() == Type.STATE &&
        r.getState().getStream().getStreamDescriptor().getName().equals(streamName)).map(AirbyteMessage::getState)
        .collect(Collectors.toList());
  }

  protected AirbyteMessage createRecord(final String stream, final String namespace, final Map<Object, Object> data) {
    return new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withData(Jsons.jsonNode(data)).withStream(stream).withNamespace(namespace));
  }

}
