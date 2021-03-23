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

package io.airbyte.integrations.source.jdbc.test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.mockito.Mockito.doCallRealMethod;
import static org.mockito.Mockito.spy;

import java.math.BigDecimal;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.models.JdbcState;
import io.airbyte.integrations.source.jdbc.models.JdbcStreamState;
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
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
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
public abstract class JdbcSourceStandardTest {

  private static final String SCHEMA_NAME = "JDBC_INTEGRATION_TEST";
  private static final String SCHEMA_NAME2 = "JDBC_INTEGRATION_TEST2";
  private static final Set<String> TEST_SCHEMAS = ImmutableSet.of(SCHEMA_NAME, SCHEMA_NAME2);

  private static final String TABLE_NAME = "ID_AND_NAME";

  private JsonNode config;
  private JdbcDatabase database;
  private AbstractJdbcSource source;
  private static String streamName;

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
   * @return source
   */
  public abstract AbstractJdbcSource getSource();

  public void setup() throws Exception {
    source = getSource();
    config = getConfig();
    final JsonNode jdbcConfig = source.toJdbcConfig(config);

    streamName = getDefaultNamespace() + "." + TABLE_NAME;

    database = Databases.createJdbcDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        getDriverClass());

    if (supportsSchemas()) {
      createSchemas();
    }

    if (getDriverClass().toLowerCase().contains("oracle")) {
      executeOracleStatement(String.format("DROP TABLE %s", getFullyQualifiedTableName(TABLE_NAME)));
    }

    database.execute(connection -> {
      connection.createStatement().execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'");
     connection.createStatement()
          .execute(String.format("CREATE TABLE %s(ID INTEGER, NAME VARCHAR(200), UPDATED_AT DATE)", getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
          String.format("INSERT INTO %s(id, name, updated_at) VALUES (1,'picard', '2004-10-19')", getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
              String.format("INSERT INTO %s(id, name, updated_at) VALUES (2, 'crusher', '2005-10-19')", getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
              String.format("INSERT INTO %s(id, name, updated_at) VALUES (3, 'vash', '2006-10-19')", getFullyQualifiedTableName(TABLE_NAME)));
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
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.FAILED)
        .withMessage("Could not connect with provided configuration.");
    assertEquals(expected, actual);
  }

  @Test
  void testDiscover() throws Exception {
    final AirbyteCatalog actual = source.discover(config);
    assertEquals(getCatalog(), filterOutOtherSchemas(actual));
  }

  private AirbyteCatalog filterOutOtherSchemas(AirbyteCatalog catalog) {
    if (supportsSchemas()) {

      final AirbyteCatalog filteredCatalog = Jsons.clone(catalog);
      filteredCatalog.setStreams(filteredCatalog.getStreams()
          .stream()
          .filter(streamName -> TEST_SCHEMAS.stream().anyMatch(schemaName -> streamName.getName().startsWith(schemaName)))
          .collect(Collectors.toList()));
      return filteredCatalog;
    } else {
      return catalog;
    }

  }

  @Test
  void testDiscoverWithMultipleSchemas() throws Exception {
    // mysql does not have a concept of schemas, so this test does not make sense for it.
    if (getDriverClass().toLowerCase().contains("mysql")) {
      return;
    }

    // add table and data to a separate schema.
    database.execute(connection -> {
      connection.createStatement().execute(
          String.format("CREATE TABLE %s(id VARCHAR(200), name VARCHAR(200))", JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));
      connection.createStatement().execute(String.format("INSERT INTO %s(id, name) VALUES (1,'picard')",
              JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));
      connection.createStatement().execute(String.format("INSERT INTO %s(id, name) VALUES (2, 'crusher')",
              JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));
      connection.createStatement().execute(String.format("INSERT INTO %s(id, name) VALUES (3, 'vash')",
              JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));
    });

    final AirbyteCatalog actual = source.discover(config);

    final AirbyteCatalog expected = getCatalog();
    expected.getStreams().add(CatalogHelpers.createAirbyteStream(JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME),
        Field.of("id", JsonSchemaPrimitive.STRING),
        Field.of("name", JsonSchemaPrimitive.STRING))
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)));
    // sort streams by name so that we are comparing lists with the same order.
    expected.getStreams().sort(Comparator.comparing(AirbyteStream::getName));
    actual.getStreams().sort(Comparator.comparing(AirbyteStream::getName));
    assertEquals(expected, filterOutOtherSchemas(actual));
  }

  @Test
  void testReadSuccess() throws Exception {
    final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(config, getConfiguredCatalog(), null));

    setEmittedAtToNull(actualMessages);

    assertEquals(getTestMessages(), actualMessages);
  }

  @Test
  void testReadOneColumn() throws Exception {
    final ConfiguredAirbyteCatalog catalog = CatalogHelpers.createConfiguredAirbyteCatalog(streamName, Field.of("ID", JsonSchemaPrimitive.NUMBER));

    final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(config, catalog, null));

    setEmittedAtToNull(actualMessages);

    final List<AirbyteMessage> expectedMessages = getTestMessages().stream()
        .map(Jsons::clone)
        .peek(m -> {
          ((ObjectNode) m.getRecord().getData()).remove("NAME");
          ((ObjectNode) m.getRecord().getData()).remove("UPDATED_AT");
        })
        .collect(Collectors.toList());
    assertEquals(expectedMessages, actualMessages);
  }

  @Test
  void testReadMultipleTables() throws Exception {
    final ConfiguredAirbyteCatalog catalog =
        new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(getConfiguredCatalog().getStreams().get(0)));
    final List<AirbyteMessage> expectedMessages = new ArrayList<>(getTestMessages());

    for (int i = 2; i < 10; i++) {
      final int iFinal = i;
      final String streamName2 = streamName + i;
      database.execute(connection -> {
        connection.createStatement()
            .execute(String.format("CREATE TABLE %s(id INTEGER, name VARCHAR(200))", getFullyQualifiedTableName(TABLE_NAME + iFinal)));
        connection.createStatement().execute(String.format("INSERT INTO %s(id, name) VALUES (1,'picard')",
            getFullyQualifiedTableName(TABLE_NAME + iFinal)));
        connection.createStatement().execute(String.format("INSERT INTO %s(id, name) VALUES (2, 'crusher')",
                getFullyQualifiedTableName(TABLE_NAME + iFinal)));
        connection.createStatement().execute(String.format("INSERT INTO %s(id, name) VALUES (3, 'vash')",
                getFullyQualifiedTableName(TABLE_NAME + iFinal)));
      });

      catalog.getStreams().add(CatalogHelpers.createConfiguredAirbyteStream(
          streamName2,
          Field.of("ID", JsonSchemaPrimitive.NUMBER),
          Field.of("NAME", JsonSchemaPrimitive.STRING)));

      final List<AirbyteMessage> secondStreamExpectedMessages = getTestMessages()
          .stream()
          .map(Jsons::clone)
          .peek(m -> {
            m.getRecord().setStream(streamName2);
            ((ObjectNode) m.getRecord().getData()).remove("UPDATED_AT");
          })
          .collect(Collectors.toList());
      expectedMessages.addAll(secondStreamExpectedMessages);
    }

    final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(config, catalog, null));

    setEmittedAtToNull(actualMessages);

    AirbyteMessage firstExpectedMsg = expectedMessages.get(0);
    AirbyteMessage firstActualMsg = actualMessages.get(0);

    boolean checkFirstAreEqual = firstExpectedMsg.equals(firstExpectedMsg);
    int hashFirstExpected = firstExpectedMsg.hashCode();
    int hashFirstActual = firstActualMsg.hashCode();
    boolean hashAreEqual =  hashFirstExpected == hashFirstActual;


    assertEquals(expectedMessages, actualMessages);
  }

  @Test
  void testTablesWithQuoting() throws Exception {
    final ConfiguredAirbyteStream streamForTableWithSpaces = createTableWithSpaces();

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        getConfiguredCatalog().getStreams().get(0),
        streamForTableWithSpaces));
    final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(config, catalog, null));

    setEmittedAtToNull(actualMessages);

    final List<AirbyteMessage> secondStreamExpectedMessages = getTestMessages()
        .stream()
        .map(Jsons::clone)
        .peek(m -> {
          m.getRecord().setStream(streamForTableWithSpaces.getStream().getName());
          ((ObjectNode) m.getRecord().getData()).set("LAST NAME", ((ObjectNode) m.getRecord().getData()).remove("NAME"));
          ((ObjectNode) m.getRecord().getData()).remove("UPDATED_AT");
        })
        .collect(Collectors.toList());
    final List<AirbyteMessage> expectedMessages = new ArrayList<>(getTestMessages());
    expectedMessages.addAll(secondStreamExpectedMessages);

    assertEquals(expectedMessages, actualMessages);
  }

  @SuppressWarnings("ResultOfMethodCallIgnored")
  @Test
  void testReadFailure() {
    final ConfiguredAirbyteStream spiedAbStream = spy(getConfiguredCatalog().getStreams().get(0));
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(spiedAbStream));
    doCallRealMethod().doThrow(new RuntimeException()).when(spiedAbStream).getStream();

    assertThrows(RuntimeException.class, () -> source.read(config, catalog, null));
  }

  @Test
  void testIncrementalNoPreviousState() throws Exception {
    incrementalCursorCheck(
        "ID",
        null,
        "3",
        Lists.newArrayList(getTestMessages()));
  }

  @Test
  void testIncrementalIntCheckCursor() throws Exception {
    incrementalCursorCheck(
        "ID",
        "2",
        "3",
        Lists.newArrayList(getTestMessages().get(2)));
  }

  @Test
  void testIncrementalStringCheckCursor() throws Exception {
    incrementalCursorCheck(
        "NAME",
        "patent",
        "vash",
        Lists.newArrayList(getTestMessages().get(0), getTestMessages().get(2)));
  }

  @Test
  void testIncrementalStringCheckCursorSpaceInColumnName() throws Exception {
    final ConfiguredAirbyteStream streamWithSpaces = createTableWithSpaces();

    final AirbyteMessage firstMessage = getTestMessages().get(0);
    firstMessage.getRecord().setStream(streamWithSpaces.getStream().getName());
    ((ObjectNode) firstMessage.getRecord().getData()).remove("UPDATED_AT");
    ((ObjectNode) firstMessage.getRecord().getData()).set("LAST NAME", ((ObjectNode) firstMessage.getRecord().getData()).remove("NAME"));

    final AirbyteMessage secondMessage = getTestMessages().get(2);
    secondMessage.getRecord().setStream(streamWithSpaces.getStream().getName());
    ((ObjectNode) secondMessage.getRecord().getData()).remove("UPDATED_AT");
    ((ObjectNode) secondMessage.getRecord().getData()).set("LAST NAME", ((ObjectNode) secondMessage.getRecord().getData()).remove("NAME"));

    Lists.newArrayList(getTestMessages().get(0), getTestMessages().get(2));

    incrementalCursorCheck(
        "LAST NAME",
        "LAST NAME",
        "patent",
        "vash",
        Lists.newArrayList(firstMessage, secondMessage),
        streamWithSpaces);
  }

  @Test
  void testIncrementalTimestampCheckCursor() throws Exception {
    incrementalCursorCheck(
        "UPDATED_AT",
        "2005-10-18T00:00:00Z",
        "2006-10-19T00:00:00Z",
        Lists.newArrayList(getTestMessages().get(1), getTestMessages().get(2)));
  }

  @Test
  void testIncrementalCursorChanges() throws Exception {
    incrementalCursorCheck(
        "ID",
        "NAME",
        // cheesing this value a little bit. in the correct implementation this initial cursor value should
        // be ignored because the cursor field changed. setting it to a value that if used, will cause
        // records to (incorrectly) be filtered out.
        "data",
        "vash",
        Lists.newArrayList(getTestMessages()));
  }

  @Test
  void testReadOneTableIncrementallyTwice() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(Lists.newArrayList("ID"));
    });

    final JdbcState state = new JdbcState().withStreams(Lists.newArrayList(new JdbcStreamState().withStreamName(streamName)));
    final List<AirbyteMessage> actualMessagesFirstSync = MoreIterators.toList(source.read(config, configuredCatalog, Jsons.jsonNode(state)));

    final Optional<AirbyteMessage> stateAfterFirstSyncOptional = actualMessagesFirstSync.stream().filter(r -> r.getType() == Type.STATE).findFirst();
    assertTrue(stateAfterFirstSyncOptional.isPresent());

    database.execute(connection -> {
      connection.createStatement().execute(
              String.format("INSERT INTO %s(id, name, updated_at) VALUES (4,'riker', '2006-10-19')", getFullyQualifiedTableName(TABLE_NAME)));
      connection.createStatement().execute(
              String.format("INSERT INTO %s(id, name, updated_at) VALUES (5, 'data', '2006-10-19')", getFullyQualifiedTableName(TABLE_NAME)));
    });

    final List<AirbyteMessage> actualMessagesSecondSync = MoreIterators
        .toList(source.read(config, configuredCatalog, stateAfterFirstSyncOptional.get().getState().getData()));

    assertEquals(2, (int) actualMessagesSecondSync.stream().filter(r -> r.getType() == Type.RECORD).count());
    final List<AirbyteMessage> expectedMessages = new ArrayList<>();
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName)
            .withData(Jsons.jsonNode(ImmutableMap.of("ID", BigDecimal.valueOf(4), "NAME", "riker", "UPDATED_AT", "2006-10-19T00:00:00Z")))));
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName)
            .withData(Jsons.jsonNode(ImmutableMap.of("ID", BigDecimal.valueOf(5), "NAME", "data", "UPDATED_AT", "2006-10-19T00:00:00Z")))));
    expectedMessages.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new JdbcState()
                .withStreams(Lists.newArrayList(new JdbcStreamState()
                    .withStreamName(streamName)
                    .withCursorField(ImmutableList.of("ID"))
                    .withCursor("5")))))));

    setEmittedAtToNull(actualMessagesSecondSync);

    assertEquals(expectedMessages, actualMessagesSecondSync);
  }

  @Test
  void testReadMultipleTablesIncrementally() throws Exception {
    final String tableName2 = TABLE_NAME + 20;
    final String streamName2 = streamName + 2;
    database.execute(ctx -> {
      ctx.createStatement().execute(String.format("CREATE TABLE %s(id INTEGER, name VARCHAR(200))", getFullyQualifiedTableName(tableName2)));
      ctx.createStatement().execute(
          String.format("INSERT INTO %s(id, name) VALUES (1,'picard')", getFullyQualifiedTableName(tableName2)));
      ctx.createStatement().execute(
              String.format("INSERT INTO %s(id, name) VALUES (2, 'crusher')", getFullyQualifiedTableName(tableName2)));
      ctx.createStatement().execute(
              String.format("INSERT INTO %s(id, name) VALUES (3, 'vash')", getFullyQualifiedTableName(tableName2)));
    });

    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
    configuredCatalog.getStreams().add(CatalogHelpers.createConfiguredAirbyteStream(
        streamName2,
        Field.of("ID", JsonSchemaPrimitive.NUMBER),
        Field.of("NAME", JsonSchemaPrimitive.STRING)));
    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(Lists.newArrayList("ID"));
    });

    final JdbcState state = new JdbcState().withStreams(Lists.newArrayList(new JdbcStreamState().withStreamName(streamName)));
    final List<AirbyteMessage> actualMessagesFirstSync = MoreIterators.toList(source.read(config, configuredCatalog, Jsons.jsonNode(state)));

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
          ((ObjectNode) m.getRecord().getData()).remove("UPDATED_AT");
        })
        .collect(Collectors.toList());
    final List<AirbyteMessage> expectedMessagesFirstSync = new ArrayList<>(getTestMessages());
    expectedMessagesFirstSync.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new JdbcState()
                .withStreams(Lists.newArrayList(
                    new JdbcStreamState()
                        .withStreamName(streamName)
                        .withCursorField(ImmutableList.of("ID"))
                        .withCursor("3"),
                    new JdbcStreamState()
                        .withStreamName(streamName2)
                        .withCursorField(ImmutableList.of("ID"))))))));
    expectedMessagesFirstSync.addAll(secondStreamExpectedMessages);
    expectedMessagesFirstSync.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new JdbcState()
                .withStreams(Lists.newArrayList(
                    new JdbcStreamState()
                        .withStreamName(streamName)
                        .withCursorField(ImmutableList.of("ID"))
                        .withCursor("3"),
                    new JdbcStreamState()
                        .withStreamName(streamName2)
                        .withCursorField(ImmutableList.of("ID"))
                        .withCursor("3")))))));
    setEmittedAtToNull(actualMessagesFirstSync);

    assertEquals(expectedMessagesFirstSync, actualMessagesFirstSync);
  }

  // when initial and final cursor fields are the same.
  private void incrementalCursorCheck(
                                      String cursorField,
                                      String initialCursorValue,
                                      String endCursorValue,
                                      List<AirbyteMessage> expectedRecordMessages)
      throws Exception {
    incrementalCursorCheck(cursorField, cursorField, initialCursorValue, endCursorValue, expectedRecordMessages);
  }

  private void incrementalCursorCheck(
                                      String initialCursorField,
                                      String cursorField,
                                      String initialCursorValue,
                                      String endCursorValue,
                                      List<AirbyteMessage> expectedRecordMessages)
      throws Exception {
    incrementalCursorCheck(initialCursorField, cursorField, initialCursorValue, endCursorValue, expectedRecordMessages,
        getConfiguredCatalog().getStreams().get(0));
  }

  private void incrementalCursorCheck(
                                      String initialCursorField,
                                      String cursorField,
                                      String initialCursorValue,
                                      String endCursorValue,
                                      List<AirbyteMessage> expectedRecordMessages,
                                      ConfiguredAirbyteStream airbyteStream)
      throws Exception {
    airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
    airbyteStream.setCursorField(Lists.newArrayList(cursorField));

    final JdbcState state = new JdbcState()
        .withStreams(Lists.newArrayList(new JdbcStreamState()
            .withStreamName(airbyteStream.getStream().getName())
            .withCursorField(ImmutableList.of(initialCursorField))
            .withCursor(initialCursorValue)));

    final ConfiguredAirbyteCatalog configuredCatalog = new ConfiguredAirbyteCatalog().withStreams(ImmutableList.of(airbyteStream));

    final List<AirbyteMessage> actualMessages = MoreIterators.toList(source.read(config, configuredCatalog, Jsons.jsonNode(state)));

    setEmittedAtToNull(actualMessages);

    final List<AirbyteMessage> expectedMessages = new ArrayList<>(expectedRecordMessages);
    expectedMessages.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(new JdbcState()
                .withStreams(Lists.newArrayList(new JdbcStreamState()
                    .withStreamName(airbyteStream.getStream().getName())
                    .withCursorField(ImmutableList.of(cursorField))
                    .withCursor(endCursorValue)))))));

    assertEquals(expectedMessages, actualMessages);
  }

  // get catalog and perform a defensive copy.
  private static ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CatalogHelpers.toDefaultConfiguredCatalog(getCatalog());
  }

  private static AirbyteCatalog getCatalog() {
    return new AirbyteCatalog().withStreams(Lists.newArrayList(CatalogHelpers.createAirbyteStream(
        streamName,
        Field.of("ID", JsonSchemaPrimitive.NUMBER),
        Field.of("NAME", JsonSchemaPrimitive.STRING),
        Field.of("UPDATED_AT", JsonSchemaPrimitive.STRING))
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))));
  }

  private static List<AirbyteMessage> getTestMessages() {
    return Lists.newArrayList(
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName)
                .withData(Jsons.jsonNode(ImmutableMap.of("ID", new BigDecimal(1), "NAME", "picard", "UPDATED_AT", "2004-10-19T00:00:00Z")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName)
                .withData(Jsons.jsonNode(ImmutableMap.of("ID", new BigDecimal(2), "NAME", "crusher", "UPDATED_AT", "2005-10-19T00:00:00Z")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName)
                .withData(Jsons.jsonNode(ImmutableMap.of("ID", new BigDecimal(3), "NAME", "vash", "UPDATED_AT", "2006-10-19T00:00:00Z")))));
  }

  private ConfiguredAirbyteStream createTableWithSpaces() throws SQLException {
    // test table name with space.
    final String tableNameWithSpaces = "id and name2";
    final String streamName2 = getDefaultNamespace() + "." + tableNameWithSpaces;
    // test column name with space.
    final String lastNameField = "last name";
    database.execute(connection -> {
      connection.createStatement().execute(String.format("CREATE TABLE %s(id INTEGER, %s VARCHAR(200))",
          getFullyQualifiedTableName(JdbcUtils.enquoteIdentifier(connection, tableNameWithSpaces)),
          JdbcUtils.enquoteIdentifier(connection, lastNameField)));
      connection.createStatement().execute(String.format("INSERT INTO %s(id, %s) VALUES (1,'picard')",
          getFullyQualifiedTableName(JdbcUtils.enquoteIdentifier(connection, tableNameWithSpaces)),
          JdbcUtils.enquoteIdentifier(connection, lastNameField)));
      connection.createStatement().execute(String.format("INSERT INTO %s(id, %s) VALUES (2, 'crusher')",
              getFullyQualifiedTableName(JdbcUtils.enquoteIdentifier(connection, tableNameWithSpaces)),
              JdbcUtils.enquoteIdentifier(connection, lastNameField)));
      connection.createStatement().execute(String.format("INSERT INTO %s(id, %s) VALUES (3, 'vash')",
              getFullyQualifiedTableName(JdbcUtils.enquoteIdentifier(connection, tableNameWithSpaces)),
              JdbcUtils.enquoteIdentifier(connection, lastNameField)));
    });

    return CatalogHelpers.createConfiguredAirbyteStream(
        streamName2,
        Field.of("id", JsonSchemaPrimitive.NUMBER),
        Field.of(lastNameField, JsonSchemaPrimitive.STRING));
  }

  private String getFullyQualifiedTableName(String tableName) {
    return JdbcUtils.getFullyQualifiedTableName(getDefaultSchemaName(), tableName);
  }

  public void executeOracleStatement(String query) throws SQLException { }

  public void createSchemas() throws SQLException {
    if (supportsSchemas()) {
      for (String schemaName : TEST_SCHEMAS) {
        if (getDriverClass().toLowerCase().contains("oracle")) {
          final String SchemaQuery = String.format("CREATE USER %s IDENTIFIED BY %s DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS", schemaName, schemaName);
          database.execute(connection -> connection.createStatement().execute(SchemaQuery));
        } else {
          final String SchemaQuery = String.format("CREATE SCHEMA %s;", schemaName);
          database.execute(connection -> connection.createStatement().execute(SchemaQuery));
        }
      }
    }
  }

  private void dropSchemas() throws SQLException {
    if (supportsSchemas()) {
      for (String schemaName : TEST_SCHEMAS) {
        final String dropSchemaQuery = String.format("DROP SCHEMA IF EXISTS %s CASCADE", schemaName);
        database.execute(connection -> connection.createStatement().execute(dropSchemaQuery));
      }
    }
  }

  private String getDefaultSchemaName() {
    return supportsSchemas() ? SCHEMA_NAME : null;
  }

  private String getDefaultNamespace() {
    // mysql does not support schemas. it namespaces using database names instead.
    if (getDriverClass().toLowerCase().contains("mysql")) {
      return config.get("database").asText();
    } else {
      return SCHEMA_NAME;
    }
  }

  private static void setEmittedAtToNull(Iterable<AirbyteMessage> messages) {
    for (AirbyteMessage actualMessage : messages) {
      if (actualMessage.getRecord() != null) {
        actualMessage.getRecord().setEmittedAt(null);
      }
    }
  }

}
