/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.cockroachdb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.*;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import java.util.*;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.CockroachContainer;

@Disabled
class CockroachDbJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest<CockroachDbSource, CockroachDbTestDatabase> {

  public static String COL_ROW_ID = "rowid";

  public static Long ID_VALUE_1 = 1L;
  public static Long ID_VALUE_2 = 2L;
  public static Long ID_VALUE_3 = 3L;
  public static Long ID_VALUE_4 = 4L;
  public static Long ID_VALUE_5 = 5L;

  static final String DB_NAME = "postgres";

  @Override
  protected String createTableQuery(final String tableName, final String columnClause, final String primaryKeyClause) {
    return String.format("CREATE TABLE " + DB_NAME + ".%s(%s %s %s)",
        tableName, columnClause, primaryKeyClause.equals("") ? "" : ",", primaryKeyClause);
  }

  @Override
  protected CockroachDbTestDatabase createTestDatabase() {
    final CockroachContainer cockroachContainer = new CockroachContainer("cockroachdb/cockroach:v20.2.18");
    cockroachContainer.start();
    return new CockroachDbTestDatabase(cockroachContainer).initialized();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  protected CockroachDbSource source() {
    return new CockroachDbSource();
  }

  @Override
  public JsonNode config() {
    return Jsons.clone(testdb.configBuilder().build());
  }

  @Override
  protected AirbyteCatalog getCatalog(final String defaultNamespace) {
    return new AirbyteCatalog().withStreams(Lists.newArrayList(
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_WITHOUT_PK,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING),
            Field.of(COL_ROW_ID, JsonSchemaType.INTEGER))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ROW_ID))),
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

  @Override
  protected List<AirbyteMessage> getTestMessages() {
    return List.of(
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName())
                .withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_1,
                        COL_NAME, "picard",
                        COL_UPDATED_AT, "2004-10-19")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName())
                .withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_2,
                        COL_NAME, "crusher",
                        COL_UPDATED_AT,
                        "2005-10-19")))),
        new AirbyteMessage().withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(streamName())
                .withNamespace(getDefaultNamespace())
                .withData(Jsons.jsonNode(Map
                    .of(COL_ID, ID_VALUE_3,
                        COL_NAME, "vash",
                        COL_UPDATED_AT, "2006-10-19")))));
  }

  @Test
  @Override
  protected void testDiscoverWithNonCursorFields() throws Exception {
    /*
     * this test is not valid for cockroach db, when table has no introduced PK it will add a hidden
     * rowid which will be taken from db , it as well present on airbyte UI thus there will be no case
     * to create a table without cursor field.
     * https://www.cockroachlabs.com/docs/stable/serial.html#auto-incrementing-is-not-always-sequential
     */
  }

  @Test
  @Override
  protected void testDiscoverWithNullableCursorFields() throws Exception {
    /*
     * this test is not valid for cockroach db, when table has no introduced PK it will add a hidden
     * rowid which will be taken from db , it as well present on airbyte UI thus there will be no case
     * to create a table without cursor field.
     * https://www.cockroachlabs.com/docs/stable/serial.html#auto-incrementing-is-not-always-sequential
     */
  }

  @Test
  @Override
  protected void testCheckFailure() throws Exception {
    final JsonNode config = config();
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake");
    ((ObjectNode) config).put(JdbcUtils.USERNAME_KEY, "fake");
    final AirbyteConnectionStatus actual = source().check(config);
    assertEquals(Status.FAILED, actual.getStatus());
  }

  @Test
  @Override
  protected void testReadOneColumn() throws Exception {
    final ConfiguredAirbyteCatalog catalog = CatalogHelpers
        .createConfiguredAirbyteCatalog(streamName(), getDefaultNamespace(),
            Field.of(COL_ID, JsonSchemaType.NUMBER));
    final List<AirbyteMessage> actualMessages = MoreIterators
        .toList(source().read(config(), catalog, null));

    setEmittedAtToNull(actualMessages);

    final List<AirbyteMessage> expectedMessages = getTestMessages().stream()
        .map(Jsons::clone)
        .peek(m -> {
          ((ObjectNode) m.getRecord().getData()).remove(COL_NAME);
          ((ObjectNode) m.getRecord().getData()).remove(COL_UPDATED_AT);
          ((ObjectNode) m.getRecord().getData()).replace(COL_ID,
              Jsons.jsonNode(m.getRecord().getData().get(COL_ID).asLong()));
        })
        .collect(Collectors.toList());
    assertTrue(expectedMessages.size() == actualMessages.size());
    assertTrue(expectedMessages.containsAll(actualMessages));
    assertTrue(actualMessages.containsAll(expectedMessages));
  }

  @Test
  @Override
  protected void testTablesWithQuoting() throws Exception {
    final ConfiguredAirbyteStream streamForTableWithSpaces = createTableWithSpaces();

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(Lists.newArrayList(
            getConfiguredCatalogWithOneStream(getDefaultNamespace()).getStreams().get(0),
            streamForTableWithSpaces));
    final List<AirbyteMessage> actualMessages = MoreIterators
        .toList(source().read(config(), catalog, null));

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
              Jsons.jsonNode(m.getRecord().getData().get(COL_ID).asLong()));
        })
        .collect(Collectors.toList());
    final List<AirbyteMessage> expectedMessages = new ArrayList<>(getTestMessages());
    expectedMessages.addAll(secondStreamExpectedMessages);

    assertTrue(expectedMessages.size() == actualMessages.size());
    assertTrue(expectedMessages.containsAll(actualMessages));
    assertTrue(actualMessages.containsAll(expectedMessages));
  }

  @Test
  @Override
  protected void testReadOneTableIncrementallyTwice() throws Exception {
    final String namespace = getDefaultNamespace();
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalogWithOneStream(namespace);
    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(Lists.newArrayList(COL_ID));
      airbyteStream.setDestinationSyncMode(DestinationSyncMode.APPEND);
    });

    final DbState state = new DbState()
        .withStreams(Lists.newArrayList(
            new DbStreamState().withStreamName(streamName()).withStreamNamespace(namespace)));
    final List<AirbyteMessage> actualMessagesFirstSync = MoreIterators
        .toList(source().read(config(), configuredCatalog, Jsons.jsonNode(state)));

    final Optional<AirbyteMessage> stateAfterFirstSyncOptional = actualMessagesFirstSync.stream()
        .filter(r -> r.getType() == Type.STATE).findFirst();
    assertTrue(stateAfterFirstSyncOptional.isPresent());

    testdb.with(String.format("INSERT INTO " + DB_NAME + ".%s(id, name, updated_at) VALUES (4,'riker', '2006-10-19')",
        getFullyQualifiedTableName(TABLE_NAME)))
        .with(String.format("INSERT INTO " + DB_NAME + ".%s(id, name, updated_at) VALUES (5, 'data', '2006-10-19')",
            getFullyQualifiedTableName(TABLE_NAME)));

    final List<AirbyteMessage> actualMessagesSecondSync = MoreIterators
        .toList(source().read(config(), configuredCatalog,
            stateAfterFirstSyncOptional.get().getState().getData()));

    assertEquals(2,
        (int) actualMessagesSecondSync.stream().filter(r -> r.getType() == Type.RECORD).count());
    final List<AirbyteMessage> expectedMessages = new ArrayList<>();
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName()).withNamespace(namespace)
            .withData(Jsons.jsonNode(ImmutableMap
                .of(COL_ID, ID_VALUE_4,
                    COL_NAME, "riker",
                    COL_UPDATED_AT, "2006-10-19")))));
    expectedMessages.add(new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName()).withNamespace(namespace)
            .withData(Jsons.jsonNode(ImmutableMap
                .of(COL_ID, ID_VALUE_5,
                    COL_NAME, "data",
                    COL_UPDATED_AT, "2006-10-19")))));
    expectedMessages.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(streamName()).withNamespace(namespace))
                .withStreamState(Jsons.jsonNode(new DbStreamState()
                    .withStreamName(streamName())
                    .withStreamNamespace(namespace)
                    .withCursor("5")
                    .withCursorRecordCount(1L)
                    .withCursorField(Collections.singletonList(COL_ID)))))
            .withData(Jsons.jsonNode(new DbState()
                .withCdc(false)
                .withStreams(Lists.newArrayList(new DbStreamState()
                    .withStreamName(streamName())
                    .withStreamNamespace(namespace)
                    .withCursorField(ImmutableList.of(COL_ID))
                    .withCursor("5")
                    .withCursorRecordCount(1L)))))));

    setEmittedAtToNull(actualMessagesSecondSync);

    assertTrue(expectedMessages.size() == actualMessagesSecondSync.size());
    assertTrue(expectedMessages.containsAll(actualMessagesSecondSync));
    assertTrue(actualMessagesSecondSync.containsAll(expectedMessages));
  }

  @Test
  @Override
  protected void testReadMultipleTables() throws Exception {
    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalogWithOneStream(
        getDefaultNamespace());
    final List<AirbyteMessage> expectedMessages = new ArrayList<>(getTestMessages());

    for (int i = 2; i < 10; i++) {
      final int iFinal = i;
      final String streamName2 = streamName() + i;
      testdb.with(createTableQuery(getFullyQualifiedTableName(TABLE_NAME + iFinal),
          "id INTEGER, name VARCHAR(200)", ""))
          .with(String.format("INSERT INTO " + DB_NAME + ".%s(id, name) VALUES (1,'picard')",
              getFullyQualifiedTableName(TABLE_NAME + iFinal)))
          .with(String.format("INSERT INTO " + DB_NAME + ".%s(id, name) VALUES (2, 'crusher')",
              getFullyQualifiedTableName(TABLE_NAME + iFinal)))
          .with(String.format("INSERT INTO " + DB_NAME + ".%s(id, name) VALUES (3, 'vash')",
              getFullyQualifiedTableName(TABLE_NAME + iFinal)));

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
                Jsons.jsonNode(m.getRecord().getData().get(COL_ID).asLong()));
          })
          .collect(Collectors.toList());
      expectedMessages.addAll(secondStreamExpectedMessages);
    }

    final List<AirbyteMessage> actualMessages = MoreIterators
        .toList(source().read(config(), catalog, null));

    setEmittedAtToNull(actualMessages);

    assertTrue(expectedMessages.size() == actualMessages.size());
    assertTrue(expectedMessages.containsAll(actualMessages));
    assertTrue(actualMessages.containsAll(expectedMessages));
  }

  @Test
  @Override
  protected void testReadMultipleTablesIncrementally() throws Exception {
    final String tableName2 = TABLE_NAME + 2;
    final String streamName2 = streamName() + 2;
    testdb.with(createTableQuery(getFullyQualifiedTableName(tableName2), "id INTEGER, name VARCHAR(200)",
        ""))
        .with(String.format("INSERT INTO " + DB_NAME + ".%s(id, name) VALUES (1,'picard')",
            getFullyQualifiedTableName(tableName2)))
        .with(String.format("INSERT INTO " + DB_NAME + ".%s(id, name) VALUES (2, 'crusher')",
            getFullyQualifiedTableName(tableName2)))
        .with(String.format("INSERT INTO " + DB_NAME + ".%s(id, name) VALUES (3, 'vash')",
            getFullyQualifiedTableName(tableName2)));

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
        .withStreams(Lists.newArrayList(
            new DbStreamState().withStreamName(streamName()).withStreamNamespace(namespace)));
    final List<AirbyteMessage> actualMessagesFirstSync = MoreIterators
        .toList(source().read(config(), configuredCatalog, Jsons.jsonNode(state)));

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
              Jsons.jsonNode(m.getRecord().getData().get(COL_ID).asLong()));
        })
        .collect(Collectors.toList());
    final List<AirbyteMessage> expectedMessagesFirstSync = new ArrayList<>(getTestMessages());
    expectedMessagesFirstSync.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withNamespace(namespace).withName(streamName()))
                .withStreamState(Jsons.jsonNode(new DbStreamState()
                    .withStreamName(streamName())
                    .withStreamNamespace(namespace)
                    .withCursor("3")
                    .withCursorRecordCount(1L)
                    .withCursorField(Collections.singletonList(COL_ID)))))
            .withData(Jsons.jsonNode(new DbState()
                .withCdc(false)
                .withStreams(Lists.newArrayList(
                    new DbStreamState()
                        .withStreamName(streamName())
                        .withStreamNamespace(namespace)
                        .withCursorField(ImmutableList.of(COL_ID))
                        .withCursor("3")
                        .withCursorRecordCount(1L),
                    new DbStreamState()
                        .withStreamName(streamName2)
                        .withStreamNamespace(namespace)
                        .withCursorField(ImmutableList.of(COL_ID))))))));

    expectedMessagesFirstSync.addAll(secondStreamExpectedMessages);
    expectedMessagesFirstSync.add(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withNamespace(namespace).withName(streamName2))
                .withStreamState(Jsons.jsonNode(new DbStreamState()
                    .withStreamName(streamName2)
                    .withStreamNamespace(namespace)
                    .withCursor("3")
                    .withCursorRecordCount(1L)
                    .withCursorField(Collections.singletonList(COL_ID)))))
            .withData(Jsons.jsonNode(new DbState()
                .withCdc(false)
                .withStreams(Lists.newArrayList(
                    new DbStreamState()
                        .withStreamName(streamName())
                        .withStreamNamespace(namespace)
                        .withCursorField(ImmutableList.of(COL_ID))
                        .withCursor("3")
                        .withCursorRecordCount(1L),
                    new DbStreamState()
                        .withStreamName(streamName2)
                        .withStreamNamespace(namespace)
                        .withCursorField(ImmutableList.of(COL_ID))
                        .withCursor("3")
                        .withCursorRecordCount(1L)))))));

    setEmittedAtToNull(actualMessagesFirstSync);

    assertTrue(expectedMessagesFirstSync.size() == actualMessagesFirstSync.size());
    assertTrue(expectedMessagesFirstSync.containsAll(actualMessagesFirstSync));
    assertTrue(actualMessagesFirstSync.containsAll(expectedMessagesFirstSync));
  }

  @Test
  @Override
  protected void testDiscoverWithMultipleSchemas() throws Exception {
    // add table and data to a separate schema.
    testdb.with(String.format("CREATE TABLE " + DB_NAME + ".%s(id VARCHAR(200), name VARCHAR(200))",
        JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)))
        .with(String.format("INSERT INTO " + DB_NAME + ".%s(id, name) VALUES ('1','picard')",
            JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)))
        .with(String.format("INSERT INTO " + DB_NAME + ".%s(id, name) VALUES ('2', 'crusher')",
            JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)))
        .with(String.format("INSERT INTO " + DB_NAME + ".%s(id, name) VALUES ('3', 'vash')",
            JdbcUtils.getFullyQualifiedTableName(SCHEMA_NAME2, TABLE_NAME)));

    final AirbyteCatalog actual = source().discover(config());

    final AirbyteCatalog expected = getCatalog(getDefaultNamespace());
    expected.getStreams().add(CatalogHelpers
        .createAirbyteStream(TABLE_NAME,
            SCHEMA_NAME2,
            Field.of(COL_ID, JsonSchemaType.STRING),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_ROW_ID, JsonSchemaType.INTEGER))
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
        .withSourceDefinedPrimaryKey(List.of(List.of(COL_ROW_ID))));

    // sort streams by name so that we are comparing lists with the same order.
    final Comparator<AirbyteStream> schemaTableCompare = Comparator
        .comparing(stream -> stream.getNamespace() + "." + stream.getName());
    expected.getStreams().sort(schemaTableCompare);
    actual.getStreams().sort(schemaTableCompare);
    assertEquals(expected, filterOutOtherSchemas(actual));
  }

}
