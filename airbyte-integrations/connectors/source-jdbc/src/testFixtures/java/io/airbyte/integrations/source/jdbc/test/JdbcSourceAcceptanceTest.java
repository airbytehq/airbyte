/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.jdbc.test;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doCallRealMethod;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import com.google.common.collect.Lists;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.math.BigDecimal;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.hamcrest.Matchers;
import org.junit.jupiter.api.Test;

/**
 * Tests that should be run on all Sources that extend the AbstractJdbcSource.
 */
// How leverage these tests:
// 1. Extend this class in the test module of the Source.
// 2. From the class that extends this one, you MUST call super.setup() in a @BeforeEach method.
// Otherwise you'll see many NPE issues. Your before each should also handle providing a fresh
// database between each test.
// 3. From the class that extends this one, implement a @AfterEach that cleans out the database
// between each test.
// 4. Then implement the abstract methods documented below.
@SuppressFBWarnings(
    value = {"MS_SHOULD_BE_FINAL"},
    justification = "The static variables are updated in sub classes for convenience, and cannot be final."
)
public abstract class JdbcSourceAcceptanceTest {

  // schema name must be randomized for each test run,
  // otherwise parallel runs can interfere with each other
  public static String SCHEMA_NAME = Strings.addRandomSuffix("jdbc_integration_test1", "_", 5).toLowerCase();
  public static String SCHEMA_NAME2 = Strings.addRandomSuffix("jdbc_integration_test2", "_", 5).toLowerCase();
  public static Set<String> TEST_SCHEMAS = ImmutableSet.of(SCHEMA_NAME, SCHEMA_NAME2);

  public static String TABLE_NAME = "id_and_name";
  public static String TABLE_NAME_WITH_SPACES = "id and name";
  public static String TABLE_NAME_WITHOUT_PK = "id_and_name_without_pk";
  public static String TABLE_NAME_COMPOSITE_PK = "full_name_composite_pk";

  public static String COL_ID = "id";
  public static String COL_NAME = "name";
  public static String COL_UPDATED_AT = "updated_at";
  public static String COL_FIRST_NAME = "first_name";
  public static String COL_LAST_NAME = "last_name";
  public static String COL_LAST_NAME_WITH_SPACE = "last name";
  public static Number ID_VALUE_1 = 1;
  public static Number ID_VALUE_2 = 2;
  public static Number ID_VALUE_3 = 3;
  public static Number ID_VALUE_4 = 4;
  public static Number ID_VALUE_5 = 5;

  public static String DROP_SCHEMA_QUERY = "DROP SCHEMA IF EXISTS %s CASCADE";
  public static String COLUMN_CLAUSE_WITH_PK = "id INTEGER, name VARCHAR(200), updated_at DATE";
  public static String COLUMN_CLAUSE_WITHOUT_PK = "id INTEGER, name VARCHAR(200), updated_at DATE";
  public static String COLUMN_CLAUSE_WITH_COMPOSITE_PK = "first_name VARCHAR(200), last_name VARCHAR(200), updated_at DATE";

  public JsonNode config;
  public DataSource dataSource;
  public JdbcDatabase database;
  public JdbcSourceOperations sourceOperations = getSourceOperations();
  public Source source;
  public static String streamName;

  /**
   * These tests write records without specifying a namespace (schema name). They will be written into
   * whatever the default schema is for the database. When they are discovered they will be namespaced
   * by the schema name (e.g. <default-schema-name>.<table_name>). Thus the source needs to tell the
   * tests what that default schema name is. If the database does not support schemas, then database
   * name should used instead.
   *
   * @return name that will be used to namespace the record.
   */
  public abstract boolean supportsSchemas();

  /**
   * A valid configuration to connect to a test database.
   *
   * @return config
   */
  public abstract JsonNode getConfig();

  /**
   * Full qualified class name of the JDBC driver for the database.
   *
   * @return driver
   */
  public abstract String getDriverClass();

  /**
   * An instance of the source that should be tests.
   *
   * @return abstract jdbc source
   */
  public abstract AbstractJdbcSource<?> getJdbcSource();

  /**
   * In some cases the Source that is being tested may be an AbstractJdbcSource, but because it is
   * decorated, Java cannot recognize it as such. In these cases, as a workaround a user can choose to
   * override getJdbcSource and have it return null. Then they can override this method with the
   * decorated source AND override getToDatabaseConfigFunction with the appropriate
   * toDatabaseConfigFunction that is hidden behind the decorator.
   *
   * @return source
   */
  public Source getSource() {
    return getJdbcSource();
  }

  /**
   * See getSource() for when to override this method.
   *
   * @return a function that maps a source's config to a jdbc config.
   */
  public Function<JsonNode, JsonNode> getToDatabaseConfigFunction() {
    return getJdbcSource()::toDatabaseConfig;
  }

  protected JdbcSourceOperations getSourceOperations() {
    return new JdbcSourceOperations();
  }

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

  protected String getJdbcParameterDelimiter() {
    return "&";
  }

  public void setup() throws Exception {
    source = getSource();
    config = getConfig();
    final JsonNode jdbcConfig = getToDatabaseConfigFunction().apply(config);

    streamName = TABLE_NAME;

    dataSource = DataSourceFactory.create(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        getDriverClass(),
        jdbcConfig.get("jdbc_url").asText(),
        JdbcUtils.parseJdbcParameters(jdbcConfig, "connection_properties", getJdbcParameterDelimiter())
    );

    database = new StreamingJdbcDatabase(dataSource,
        JdbcUtils.getDefaultSourceOperations(),
        AdaptiveStreamingQueryConfig::new
    );

    if (supportsSchemas()) {
      createSchemas();
    }

    if (getDriverClass().toLowerCase().contains("oracle")) {
      database.execute(connection -> connection.createStatement()
          .execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'"));
    }

    database.execute(connection -> {

      connection.createStatement().execute(
          createTableQuery(getFullyQualifiedTableName(TABLE_NAME), COLUMN_CLAUSE_WITH_PK,
              primaryKeyClause(Collections.singletonList("id"))));
      connection.createStatement().execute(
          String.format("INSERT INTO %s(id, name, updated_at) VALUES (1,'picard', '2004-10-19')",
              getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
          String.format("INSERT INTO %s(id, name, updated_at) VALUES (2, 'crusher', '2005-10-19')",
              getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
          String.format("INSERT INTO %s(id, name, updated_at) VALUES (3, 'vash', '2006-10-19')",
              getFullyQualifiedTableName(TABLE_NAME)));

      connection.createStatement().execute(
          createTableQuery(getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK),
              COLUMN_CLAUSE_WITHOUT_PK, ""));
      connection.createStatement().execute(
          String.format("INSERT INTO %s(id, name, updated_at) VALUES (1,'picard', '2004-10-19')",
              getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK)));
      connection.createStatement().execute(
          String.format("INSERT INTO %s(id, name, updated_at) VALUES (2, 'crusher', '2005-10-19')",
              getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK)));
      connection.createStatement().execute(
          String.format("INSERT INTO %s(id, name, updated_at) VALUES (3, 'vash', '2006-10-19')",
              getFullyQualifiedTableName(TABLE_NAME_WITHOUT_PK)));

      connection.createStatement().execute(
          createTableQuery(getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK),
              COLUMN_CLAUSE_WITH_COMPOSITE_PK,
              primaryKeyClause(ImmutableList.of("first_name", "last_name"))));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(first_name, last_name, updated_at) VALUES ('first' ,'picard', '2004-10-19')",
              getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(first_name, last_name, updated_at) VALUES ('second', 'crusher', '2005-10-19')",
              getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK)));
      connection.createStatement().execute(
          String.format(
              "INSERT INTO %s(first_name, last_name, updated_at) VALUES  ('third', 'vash', '2006-10-19')",
              getFullyQualifiedTableName(TABLE_NAME_COMPOSITE_PK)));

    });
  }

  public void tearDown() throws SQLException {
    dropSchemas();
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source.spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  @Test
  void testCheckSuccess() throws Exception {
    final AirbyteConnectionStatus actual = source.check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @Test
  void testCheckFailure() throws Exception {
    ((ObjectNode) config).put("password", "fake");
    final AirbyteConnectionStatus actual = source.check(config);
    assertEquals(Status.FAILED, actual.getStatus());
  }

  @Test
  void testDiscover() throws Exception {
    final AirbyteCatalog actual = filterOutOtherSchemas(source.discover(config));
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
  void testDiscoverWithMultipleSchemas() throws Exception {
    // clickhouse and mysql do not have a concept of schemas, so this test does not make sense for them.
    if (getDriverClass().toLowerCase().contains("mysql") || getDriverClass().toLowerCase().contains("clickhouse")) {
      return;
    }

    // add table and data to a separate schema.
    database.execute(connection -> {
      connection.createStatement().execute(
          String.format("CREATE TABLE %s(id VARCHAR(200), name VARCHAR(200))",
              sourceOperations.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));
      connection.createStatement()
          .execute(String.format("INSERT INTO %s(id, name) VALUES ('1','picard')",
              sourceOperations.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));
      connection.createStatement()
          .execute(String.format("INSERT INTO %s(id, name) VALUES ('2', 'crusher')",
              sourceOperations.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));
      connection.createStatement()
          .execute(String.format("INSERT INTO %s(id, name) VALUES ('3', 'vash')",
              sourceOperations.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));
    });

    final AirbyteCatalog actual = source.discover(config);

    final AirbyteCatalog expected = getCatalog(getDefaultNamespace());
    expected.getStreams().add(CatalogHelpers
        .createAirbyteStream(TABLE_NAME,
            SCHEMA_NAME2,
            Field.of(COL_ID, JsonSchemaType.STRING),
            Field.of(COL_NAME, JsonSchemaType.STRING))
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)));
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
            source.read(config, getConfiguredCatalogWithOneStream(getDefaultNamespace()), null));

    setEmittedAtToNull(actualMessages);
    final List<AirbyteMessage> expectedMessages = getTestMessages();
    assertThat(expectedMessages, Matchers.containsInAnyOrder(actualMessages.toArray()));
    assertThat(actualMessages, Matchers.containsInAnyOrder(expectedMessages.toArray()));
  }

  @Test
  void testReadOneColumn() throws Exception {
    final ConfiguredAirbyteCatalog catalog = CatalogHelpers
        .createConfiguredAirbyteCatalog(streamName, getDefaultNamespace(), Field.of(COL_ID, JsonSchemaType.NUMBER));
    final List<AirbyteMessage> actualMessages = MoreIterators
        .toList(source.read(config, catalog, null));

    setEmittedAtToNull(actualMessages);

    final List<AirbyteMessage> expectedMessages = getTestMessages().stream()
        .map(Jsons::clone)
        .peek(m -> {
          ((ObjectNode) m.getRecord().getData()).remove(COL_NAME);
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              convertIdBasedOnDatabase(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());
    assertTrue(expectedMessages.size() == actualMessages.size());
    assertTrue(expectedMessages.containsAll(actualMessages));
    assertTrue(actualMessages.containsAll(expectedMessages));
  }

  @Test
  void testReadMultipleTables() throws Exception {
    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalogWithOneStream(
        getDefaultNamespace());
    final List<AirbyteMessage> expectedMessages = new ArrayList<>(getTestMessages());

    for (int i = 2; i < 10; i++) {
      final int iFinal = i;
      final String streamName2 = streamName + i;
      database.execute(connection -> {
        connection.createStatement()
            .execute(
                createTableQuery(getFullyQualifiedTableName(TABLE_NAME + iFinal),
                    "id INTEGER, name VARCHAR(200)", ""));
        connection.createStatement()
            .execute(String.format("INSERT INTO %s(id, name) VALUES (1,'picard')",
                getFullyQualifiedTableName(TABLE_NAME + iFinal)));
        connection.createStatement()
            .execute(String.format("INSERT INTO %s(id, name) VALUES (2, 'crusher')",
                getFullyQualifiedTableName(TABLE_NAME + iFinal)));
        connection.createStatement()
            .execute(String.format("INSERT INTO %s(id, name) VALUES (3, 'vash')",
                getFullyQualifiedTableName(TABLE_NAME + iFinal)));
      });
      catalog.getStreams().add(CatalogHelpers.createConfiguredAirbyteStream(
          streamName2,
          getDefaultNamespace(),
          Field.of(COL_ID, JsonSchemaType.NUMBER),
          Field.of(COL_NAME, JsonSchemaType.STRING)));

      final List<AirbyteMessage> secondStreamExpectedMessages = getTestMessages()
          .stream()
          .map(Jsons::clone)
          .peek(m -> {
            m.getRecord().setStream(streamName2);
            m.getRecord().setNamespace(getDefaultNamespace());
            ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
            ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
                convertIdBasedOnDatabase(m.getRecord().getData().get(COL_ID).asInt()));
          })
          .collect(Collectors.toList());
      expectedMessages.addAll(secondStreamExpectedMessages);
    }

    final List<AirbyteMessage> actualMessages = MoreIterators
        .toList(source.read(config, catalog, null));

    setEmittedAtToNull(actualMessages);

    assertTrue(expectedMessages.size() == actualMessages.size());
    assertTrue(expectedMessages.containsAll(actualMessages));
    assertTrue(actualMessages.containsAll(expectedMessages));
  }

  @Test
  void testTablesWithQuoting() throws Exception {
    final ConfiguredAirbyteStream streamForTableWithSpaces = createTableWithSpaces();

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(Lists.newArrayList(
            getConfiguredCatalogWithOneStream(getDefaultNamespace()).getStreams().get(0),
            streamForTableWithSpaces));
    final List<AirbyteMessage> actualMessages = MoreIterators
        .toList(source.read(config, catalog, null));

    setEmittedAtToNull(actualMessages);

    final List<AirbyteMessage> secondStreamExpectedMessages = getTestMessages()
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
    final List<AirbyteMessage> expectedMessages = new ArrayList<>(getTestMessages());
    expectedMessages.addAll(secondStreamExpectedMessages);

    assertTrue(expectedMessages.size() == actualMessages.size());
    assertTrue(expectedMessages.containsAll(actualMessages));
    assertTrue(actualMessages.containsAll(expectedMessages));
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testReadFailure() {
    final ConfiguredAirbyteStream spiedAbStream = spy(
        getConfiguredCatalogWithOneStream(getDefaultNamespace()).getStreams().get(0));
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(Lists.newArrayList(spiedAbStream));
    doCallRealMethod().doThrow(new RuntimeException()).when(spiedAbStream).getStream();

    assertThrows(RuntimeException.class, () -> source.read(config, catalog, null));
  }

  @Test
  void testIncrementalNoPreviousState() throws Exception {
    incrementalCursorCheck(
        COL_ID,
        null,
        "3",
        Lists.newArrayList(getTestMessages()));
  }

  @Test
  void testIncrementalIntCheckCursor() throws Exception {
    incrementalCursorCheck(
        COL_ID,
        "2",
        "3",
        Lists.newArrayList(getTestMessages().get(2)));
  }

  @Test
  void testIncrementalStringCheckCursor() throws Exception {
    incrementalCursorCheck(
        COL_NAME,
        "patent",
        "vash",
        Lists.newArrayList(getTestMessages().get(0), getTestMessages().get(2)));
  }

  @Test
  void testIncrementalStringCheckCursorSpaceInColumnName() throws Exception {
    final ConfiguredAirbyteStream streamWithSpaces = createTableWithSpaces();

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

    Lists.newArrayList(getTestMessages().get(0), getTestMessages().get(2));

    incrementalCursorCheck(
        COL_LAST_NAME_WITH_SPACE,
        COL_LAST_NAME_WITH_SPACE,
        "patent",
        "vash",
        Lists.newArrayList(firstMessage, secondMessage),
        streamWithSpaces);
  }

  @Test
  void testIncrementalTimestampCheckCursor() throws Exception {
    incrementalCursorCheck(
        COL_UPDATED_AT,
        "2005-10-18T00:00:00Z",
        "2006-10-19T00:00:00Z",
        Lists.newArrayList(getTestMessages().get(1), getTestMessages().get(2)));
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
        Lists.newArrayList(getTestMessages()));
  }

  @Test
  void testReadOneTableIncrementallyTwice() throws Exception {
    final String namespace = getDefaultNamespace();
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalogWithOneStream(namespace);
    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(Lists.newArrayList(COL_ID));
      airbyteStream.setDestinationSyncMode(DestinationSyncMode.APPEND);
    });

    final DbState state = new DbState()
        .withStreams(Lists.newArrayList(new DbStreamState().withStreamName(streamName).withStreamNamespace(namespace)));
    final List<AirbyteMessage> actualMessagesFirstSync = MoreIterators
        .toList(source.read(config, configuredCatalog, Jsons.jsonNode(state)));

    final Optional<AirbyteMessage> stateAfterFirstSyncOptional = actualMessagesFirstSync.stream()
        .filter(r -> r.getType() == Type.STATE).findFirst();
    assertTrue(stateAfterFirstSyncOptional.isPresent());

    database.execute(connection -> {
      connection.createStatement().execute(
          String.format("INSERT INTO %s(id, name, updated_at) VALUES (4,'riker', '2006-10-19')",
              getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
          String.format("INSERT INTO %s(id, name, updated_at) VALUES (5, 'data', '2006-10-19')",
              getFullyQualifiedTableName(TABLE_NAME)));
    });

    final List<AirbyteMessage> actualMessagesSecondSync = MoreIterators
        .toList(source.read(config, configuredCatalog,
            stateAfterFirstSyncOptional.get().getState().getData()));

    assertEquals(2,
        (int) actualMessagesSecondSync.stream().filter(r -> r.getType() == Type.RECORD).count());
    final List<AirbyteMessage> expectedMessages = new ArrayList<>();
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace)
            .withData(Jsons.jsonNode(ImmutableMap
                .of(COL_ID, ID_VALUE_4,
                    COL_NAME, "riker",
                    COL_UPDATED_AT, "2006-10-19T00:00:00Z")))));
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace)
            .withData(Jsons.jsonNode(ImmutableMap
                .of(COL_ID, ID_VALUE_5,
                    COL_NAME, "data",
                    COL_UPDATED_AT, "2006-10-19T00:00:00Z")))));
    expectedMessages.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new DbState()
                .withCdc(false)
                .withStreams(Lists.newArrayList(new DbStreamState()
                    .withStreamName(streamName)
                    .withStreamNamespace(namespace)
                    .withCursorField(ImmutableList.of(COL_ID))
                    .withCursor("5")))))));

    setEmittedAtToNull(actualMessagesSecondSync);

    assertTrue(expectedMessages.size() == actualMessagesSecondSync.size());
    assertTrue(expectedMessages.containsAll(actualMessagesSecondSync));
    assertTrue(actualMessagesSecondSync.containsAll(expectedMessages));
  }

  @Test
  void testReadMultipleTablesIncrementally() throws Exception {
    final String tableName2 = TABLE_NAME + 2;
    final String streamName2 = streamName + 2;
    database.execute(ctx -> {
      ctx.createStatement().execute(
          createTableQuery(getFullyQualifiedTableName(tableName2), "id INTEGER, name VARCHAR(200)", ""));
      ctx.createStatement().execute(
          String.format("INSERT INTO %s(id, name) VALUES (1,'picard')",
              getFullyQualifiedTableName(tableName2)));
      ctx.createStatement().execute(
          String.format("INSERT INTO %s(id, name) VALUES (2, 'crusher')",
              getFullyQualifiedTableName(tableName2)));
      ctx.createStatement().execute(
          String.format("INSERT INTO %s(id, name) VALUES (3, 'vash')",
              getFullyQualifiedTableName(tableName2)));
    });

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
      airbyteStream.setCursorField(Lists.newArrayList(COL_ID));
      airbyteStream.setDestinationSyncMode(DestinationSyncMode.APPEND);
    });

    final DbState state = new DbState()
        .withStreams(Lists.newArrayList(new DbStreamState().withStreamName(streamName).withStreamNamespace(namespace)));
    final List<AirbyteMessage> actualMessagesFirstSync = MoreIterators
        .toList(source.read(config, configuredCatalog, Jsons.jsonNode(state)));

    // get last state message.
    final Optional<AirbyteMessage> stateAfterFirstSyncOptional = actualMessagesFirstSync.stream()
        .filter(r -> r.getType() == Type.STATE)
        .reduce((first, second) -> second);
    assertTrue(stateAfterFirstSyncOptional.isPresent());

    // we know the second streams messages are the same as the first minus the updated at column. so we
    // cheat and generate the expected messages off of the first expected messages.
    final List<AirbyteMessage> secondStreamExpectedMessages = getTestMessages()
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamName2);
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              convertIdBasedOnDatabase(m.getRecord().getData().get(COL_ID).asInt()));
        })
        .collect(Collectors.toList());
    final List<AirbyteMessage> expectedMessagesFirstSync = new ArrayList<>(getTestMessages());
    expectedMessagesFirstSync.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new DbState()
                .withCdc(false)
                .withStreams(Lists.newArrayList(
                    new DbStreamState()
                        .withStreamName(streamName)
                        .withStreamNamespace(namespace)
                        .withCursorField(ImmutableList.of(COL_ID))
                        .withCursor("3"),
                    new DbStreamState()
                        .withStreamName(streamName2)
                        .withStreamNamespace(namespace)
                        .withCursorField(ImmutableList.of(COL_ID))))))));

    expectedMessagesFirstSync.addAll(secondStreamExpectedMessages);
    expectedMessagesFirstSync.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new DbState()
                .withCdc(false)
                .withStreams(Lists.newArrayList(
                    new DbStreamState()
                        .withStreamName(streamName)
                        .withStreamNamespace(namespace)
                        .withCursorField(ImmutableList.of(COL_ID))
                        .withCursor("3"),
                    new DbStreamState()
                        .withStreamName(streamName2)
                        .withStreamNamespace(namespace)
                        .withCursorField(ImmutableList.of(COL_ID))
                        .withCursor("3")))))));

    setEmittedAtToNull(actualMessagesFirstSync);

    assertTrue(expectedMessagesFirstSync.size() == actualMessagesFirstSync.size());
    assertTrue(expectedMessagesFirstSync.containsAll(actualMessagesFirstSync));
    assertTrue(actualMessagesFirstSync.containsAll(expectedMessagesFirstSync));
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

  private void incrementalCursorCheck(
                                      final String initialCursorField,
                                      final String cursorField,
                                      final String initialCursorValue,
                                      final String endCursorValue,
                                      final List<AirbyteMessage> expectedRecordMessages,
                                      final ConfiguredAirbyteStream airbyteStream)
      throws Exception {
    airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
    airbyteStream.setCursorField(Lists.newArrayList(cursorField));
    airbyteStream.setDestinationSyncMode(DestinationSyncMode.APPEND);

    final DbState state = new DbState()
        .withStreams(Lists.newArrayList(new DbStreamState()
            .withStreamName(airbyteStream.getStream().getName())
            .withStreamNamespace(airbyteStream.getStream().getNamespace())
            .withCursorField(ImmutableList.of(initialCursorField))
            .withCursor(initialCursorValue)));

    final ConfiguredAirbyteCatalog configuredCatalog = new ConfiguredAirbyteCatalog()
        .withStreams(ImmutableList.of(airbyteStream));

    final List<AirbyteMessage> actualMessages = MoreIterators
        .toList(source.read(config, configuredCatalog, Jsons.jsonNode(state)));

    setEmittedAtToNull(actualMessages);

    final List<AirbyteMessage> expectedMessages = new ArrayList<>(expectedRecordMessages);
    expectedMessages.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new DbState()
                .withCdc(false)
                .withStreams(Lists.newArrayList(new DbStreamState()
                    .withStreamName(airbyteStream.getStream().getName())
                    .withStreamNamespace(airbyteStream.getStream().getNamespace())
                    .withCursorField(ImmutableList.of(cursorField))
                    .withCursor(endCursorValue)))))));

    assertTrue(expectedMessages.size() == actualMessages.size());
    assertTrue(expectedMessages.containsAll(actualMessages));
    assertTrue(actualMessages.containsAll(expectedMessages));
  }

  // get catalog and perform a defensive copy.
  protected ConfiguredAirbyteCatalog getConfiguredCatalogWithOneStream(final String defaultNamespace) {
    final ConfiguredAirbyteCatalog catalog = CatalogHelpers.toDefaultConfiguredCatalog(getCatalog(defaultNamespace));
    // Filter to only keep the main stream name as configured stream
    catalog.withStreams(
        catalog.getStreams().stream().filter(s -> s.getStream().getName().equals(streamName))
            .collect(Collectors.toList()));
    return catalog;
  }

  protected AirbyteCatalog getCatalog(final String defaultNamespace) {
    return new AirbyteCatalog().withStreams(Lists.newArrayList(
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.NUMBER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_WITHOUT_PK,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.NUMBER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(Collections.emptyList()),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_COMPOSITE_PK,
            defaultNamespace,
            Field.of(COL_FIRST_NAME, JsonSchemaType.STRING),
            Field.of(COL_LAST_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(
                List.of(List.of(COL_FIRST_NAME), List.of(COL_LAST_NAME)))));
  }

  protected List<AirbyteMessage> getTestMessages() {
    return Lists.newArrayList(
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(ImmutableMap
                    .of(COL_ID, ID_VALUE_1,
                        COL_NAME, "picard",
                        COL_UPDATED_AT, "2004-10-19T00:00:00Z")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(ImmutableMap
                    .of(COL_ID, ID_VALUE_2,
                        COL_NAME, "crusher",
                        COL_UPDATED_AT,
                        "2005-10-19T00:00:00Z")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(ImmutableMap
                    .of(COL_ID, ID_VALUE_3,
                        COL_NAME, "vash",
                        COL_UPDATED_AT, "2006-10-19T00:00:00Z")))));
  }

  protected ConfiguredAirbyteStream createTableWithSpaces() throws SQLException {
    final String tableNameWithSpaces = TABLE_NAME_WITH_SPACES + "2";
    final String streamName2 = tableNameWithSpaces;

    database.execute(connection -> {
      connection.createStatement()
          .execute(
              createTableQuery(getFullyQualifiedTableName(
                  sourceOperations.enquoteIdentifier(connection, tableNameWithSpaces)),
                  "id INTEGER, " + sourceOperations
                      .enquoteIdentifier(connection, COL_LAST_NAME_WITH_SPACE)
                      + " VARCHAR(200)",
                  ""));
      connection.createStatement()
          .execute(String.format("INSERT INTO %s(id, %s) VALUES (1,'picard')",
              getFullyQualifiedTableName(
                  sourceOperations.enquoteIdentifier(connection, tableNameWithSpaces)),
              sourceOperations.enquoteIdentifier(connection, COL_LAST_NAME_WITH_SPACE)));
      connection.createStatement()
          .execute(String.format("INSERT INTO %s(id, %s) VALUES (2, 'crusher')",
              getFullyQualifiedTableName(
                  sourceOperations.enquoteIdentifier(connection, tableNameWithSpaces)),
              sourceOperations.enquoteIdentifier(connection, COL_LAST_NAME_WITH_SPACE)));
      connection.createStatement()
          .execute(String.format("INSERT INTO %s(id, %s) VALUES (3, 'vash')",
              getFullyQualifiedTableName(
                  sourceOperations.enquoteIdentifier(connection, tableNameWithSpaces)),
              sourceOperations.enquoteIdentifier(connection, COL_LAST_NAME_WITH_SPACE)));
    });

    return CatalogHelpers.createConfiguredAirbyteStream(
        streamName2,
        getDefaultNamespace(),
        Field.of(COL_ID, JsonSchemaType.NUMBER),
        Field.of(COL_LAST_NAME_WITH_SPACE, JsonSchemaType.STRING));
  }

  public String getFullyQualifiedTableName(final String tableName) {
    return sourceOperations.getFullyQualifiedTableName(getDefaultSchemaName(), tableName);
  }

  public void createSchemas() throws SQLException {
    if (supportsSchemas()) {
      for (final String schemaName : TEST_SCHEMAS) {
        final String createSchemaQuery = String.format("CREATE SCHEMA %s;", schemaName);
        database.execute(connection -> connection.createStatement().execute(createSchemaQuery));
      }
    }
  }

  public void dropSchemas() throws SQLException {
    if (supportsSchemas()) {
      for (final String schemaName : TEST_SCHEMAS) {
        final String dropSchemaQuery = String
            .format(DROP_SCHEMA_QUERY, schemaName);
        database.execute(connection -> connection.createStatement().execute(dropSchemaQuery));
      }
    }
  }

  private JsonNode convertIdBasedOnDatabase(final int idValue) {
    final var driverClass = getDriverClass().toLowerCase();
    if (driverClass.contains("oracle") || driverClass.contains("snowflake")) {
      return Jsons.jsonNode(BigDecimal.valueOf(idValue));
    } else {
      return Jsons.jsonNode(idValue);
    }
  }

  private String getDefaultSchemaName() {
    return supportsSchemas() ? SCHEMA_NAME : null;
  }

  protected String getDefaultNamespace() {
    // mysql does not support schemas. it namespaces using database names instead.
    if (getDriverClass().toLowerCase().contains("mysql") || getDriverClass().toLowerCase().contains("clickhouse")) {
      return config.get("database").asText();
    } else {
      return SCHEMA_NAME;
    }
  }

  protected static void setEmittedAtToNull(final Iterable<AirbyteMessage> messages) {
    for (final AirbyteMessage actualMessage : messages) {
      if (actualMessage.getRecord() != null) {
        actualMessage.getRecord().setEmittedAt(null);
      }
    }
  }

}
