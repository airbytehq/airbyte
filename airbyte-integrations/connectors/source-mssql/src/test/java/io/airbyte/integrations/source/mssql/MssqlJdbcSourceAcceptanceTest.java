/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;
import static io.airbyte.integrations.source.mssql.initialsync.MssqlInitialLoadStateManager.STATE_TYPE_KEY;
import static java.util.stream.Collectors.toList;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.cdk.integrations.source.relationaldb.models.CursorBasedStatus;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.cdk.integrations.source.relationaldb.models.InternalModels.StateType;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStateStats;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

@edu.umd.cs.findbugs.annotations.SuppressWarnings(value = "NP_NULL_ON_SOME_PATH")
public class MssqlJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest<MssqlSource, MsSQLTestDatabase> {

  protected static final String USERNAME_WITHOUT_PERMISSION = "new_user";
  protected static final String PASSWORD_WITHOUT_PERMISSION = "password_3435!";

  static {
    // In mssql, timestamp is generated automatically, so we need to use
    // the datetime type instead so that we can set the value manually.
    COL_TIMESTAMP_TYPE = "DATETIME2";
  }

  @Override
  protected JsonNode config() {
    return testdb.testConfigBuilder()
        .withoutSsl()
        .build();
  }

  @Override
  protected MssqlSource source() {
    return new MssqlSource();
  }

  @Override
  protected MsSQLTestDatabase createTestDatabase() {
    return MsSQLTestDatabase.in(BaseImage.MSSQL_2022);
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  protected void maybeSetShorterConnectionTimeout(final JsonNode config) {
    ((ObjectNode) config).put(JdbcUtils.JDBC_URL_PARAMS_KEY, "loginTimeout=1");
  }

  @Test
  void testCheckIncorrectPasswordFailure() throws Exception {
    final var config = config();
    maybeSetShorterConnectionTimeout(config);
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake");
    final AirbyteConnectionStatus status = source().check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: S0001; Error code: 18456;"), status.getMessage());
  }

  @Test
  public void testCheckIncorrectUsernameFailure() throws Exception {
    final var config = config();
    maybeSetShorterConnectionTimeout(config);
    ((ObjectNode) config).put(JdbcUtils.USERNAME_KEY, "fake");
    final AirbyteConnectionStatus status = source().check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: S0001; Error code: 18456;"), status.getMessage());
  }

  @Test
  public void testCheckIncorrectHostFailure() throws Exception {
    final var config = config();
    maybeSetShorterConnectionTimeout(config);
    ((ObjectNode) config).put(JdbcUtils.HOST_KEY, "localhost2");
    final AirbyteConnectionStatus status = source().check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 08S01;"), status.getMessage());
  }

  @Test
  public void testCheckIncorrectPortFailure() throws Exception {
    final var config = config();
    maybeSetShorterConnectionTimeout(config);
    ((ObjectNode) config).put(JdbcUtils.PORT_KEY, "0000");
    final AirbyteConnectionStatus status = source().check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 08S01;"), status.getMessage());
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() throws Exception {
    final var config = config();
    maybeSetShorterConnectionTimeout(config);
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, "wrongdatabase");
    final AirbyteConnectionStatus status = source().check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: S0001; Error code: 4060;"), status.getMessage());
  }

  @Test
  public void testUserHasNoPermissionToDataBase() throws Exception {
    final var config = config();
    maybeSetShorterConnectionTimeout(config);
    testdb.with("CREATE LOGIN %s WITH PASSWORD = '%s'; ", USERNAME_WITHOUT_PERMISSION, PASSWORD_WITHOUT_PERMISSION);
    ((ObjectNode) config).put(JdbcUtils.USERNAME_KEY, USERNAME_WITHOUT_PERMISSION);
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, PASSWORD_WITHOUT_PERMISSION);
    final AirbyteConnectionStatus status = source().check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: S0001; Error code: 4060;"), status.getMessage());
  }

  @Test
  @Override
  protected void testReadMultipleTablesIncrementally() throws Exception {
    final var config = config();
    ((ObjectNode) config).put(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1);
    final String streamOneName = TABLE_NAME + "one";
    // Create a fresh first table
    testdb.with("CREATE TABLE %s (\n"
        + "    id INT NOT NULL PRIMARY KEY,\n"
        + "    name VARCHAR(50) NOT NULL,\n"
        + "    updated_at DATE NOT NULL\n"
        + ");", getFullyQualifiedTableName(streamOneName))
        .with("INSERT INTO %s(id, name, updated_at) VALUES (1, 'picard', '2004-10-19')",
            getFullyQualifiedTableName(streamOneName))
        .with("INSERT INTO %s(id, name, updated_at) VALUES (2, 'crusher', '2005-10-19')",
            getFullyQualifiedTableName(streamOneName))
        .with("INSERT INTO %s(id, name, updated_at) VALUES (3, 'vash', '2006-10-19')",
            getFullyQualifiedTableName(streamOneName));

    // Create a fresh second table
    final String streamTwoName = TABLE_NAME + "two";
    final String streamTwoFullyQualifiedName = getFullyQualifiedTableName(streamTwoName);
    // Insert records into second table
    testdb.with("CREATE TABLE %s (\n"
        + "    id INT NOT NULL PRIMARY KEY,\n"
        + "    name VARCHAR(50) NOT NULL,\n"
        + "    updated_at DATE NOT NULL\n"
        + ");", streamTwoFullyQualifiedName)
        .with("INSERT INTO %s (id, name, updated_at) VALUES (40, 'Jean Luc','2006-10-19')",
            streamTwoFullyQualifiedName)
        .with("INSERT INTO %s (id, name, updated_at) VALUES (41, 'Groot', '2006-10-19')",
            streamTwoFullyQualifiedName)
        .with("INSERT INTO %s (id, name, updated_at) VALUES (42, 'Thanos','2006-10-19')",
            streamTwoFullyQualifiedName);

    final List<AirbyteMessage> streamOneExpectedRecords = Arrays.asList(
        createRecord(streamOneName, getDefaultNamespace(), Map
            .of(COL_ID, ID_VALUE_1,
                COL_NAME, "picard",
                COL_UPDATED_AT, "2004-10-19")),
        createRecord(streamOneName, getDefaultNamespace(), Map
            .of(COL_ID, ID_VALUE_2,
                COL_NAME, "crusher",
                COL_UPDATED_AT,
                "2005-10-19")),
        createRecord(streamOneName, getDefaultNamespace(), Map
            .of(COL_ID, ID_VALUE_3,
                COL_NAME, "vash",
                COL_UPDATED_AT, "2006-10-19")));

    // Create records list that we expect to see in the state message
    final List<AirbyteMessage> streamTwoExpectedRecords = Arrays.asList(
        createRecord(streamTwoName, getDefaultNamespace(), ImmutableMap.of(
            COL_ID, 40,
            COL_NAME, "Jean Luc",
            COL_UPDATED_AT, "2006-10-19")),
        createRecord(streamTwoName, getDefaultNamespace(), ImmutableMap.of(
            COL_ID, 41,
            COL_NAME, "Groot",
            COL_UPDATED_AT, "2006-10-19")),
        createRecord(streamTwoName, getDefaultNamespace(), ImmutableMap.of(
            COL_ID, 42,
            COL_NAME, "Thanos",
            COL_UPDATED_AT, "2006-10-19")));

    // Prep and create a configured catalog to perform sync
    final AirbyteStream streamOne = getAirbyteStream(streamOneName, getDefaultNamespace());
    final AirbyteStream streamTwo = getAirbyteStream(streamTwoName, getDefaultNamespace());

    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(
        new AirbyteCatalog().withStreams(List.of(streamOne, streamTwo)));
    configuredCatalog.getStreams().forEach(airbyteStream -> {
      airbyteStream.setSyncMode(SyncMode.INCREMENTAL);
      airbyteStream.setCursorField(List.of(COL_ID));
      airbyteStream.setDestinationSyncMode(DestinationSyncMode.APPEND);
      airbyteStream.withPrimaryKey(List.of(List.of(COL_ID)));
    });

    // Perform initial sync
    final List<AirbyteMessage> messagesFromFirstSync = MoreIterators
        .toList(source().read(config, configuredCatalog, null));

    final List<AirbyteMessage> recordsFromFirstSync = filterRecords(messagesFromFirstSync);

    setEmittedAtToNull(messagesFromFirstSync);
    // All records in the 2 configured streams should be present
    assertThat(filterRecords(recordsFromFirstSync)).containsExactlyElementsOf(
        Stream.concat(streamOneExpectedRecords.stream().parallel(),
            streamTwoExpectedRecords.stream().parallel()).collect(toList()));

    final List<AirbyteStateMessage> actualFirstSyncState = extractStateMessage(messagesFromFirstSync);
    // Since we are emitting a state message after each record, we should have 1 state for each record -
    // 3 from stream1 and 3 from stream2
    assertEquals(6, actualFirstSyncState.size());

    // The expected state type should be 2 ordered_column's and the last one being cursor_based
    final List<String> expectedStateTypesFromFirstSync = List.of("ordered_column", "ordered_column", "cursor_based");
    final List<String> stateTypeOfStreamOneStatesFromFirstSync =
        extractSpecificFieldFromCombinedMessages(messagesFromFirstSync, streamOneName, STATE_TYPE_KEY);
    final List<String> stateTypeOfStreamTwoStatesFromFirstSync =
        extractSpecificFieldFromCombinedMessages(messagesFromFirstSync, streamTwoName, STATE_TYPE_KEY);
    // It should be the same for stream1 and stream2
    assertEquals(stateTypeOfStreamOneStatesFromFirstSync, expectedStateTypesFromFirstSync);
    assertEquals(stateTypeOfStreamTwoStatesFromFirstSync, expectedStateTypesFromFirstSync);

    // Create the expected ordered_column values that we should see
    final List<String> expectedOrderedColumnValueFromFirstSync = List.of("1", "2");
    final List<String> orderedColumnValuesOfStreamOneFromFirstSync =
        extractSpecificFieldFromCombinedMessages(messagesFromFirstSync, streamOneName, "ordered_col_val");
    final List<String> orderedColumnValuesOfStreamTwoFromFirstSync =
        extractSpecificFieldFromCombinedMessages(messagesFromFirstSync, streamOneName, "ordered_col_val");

    // Verifying each element and its index to match.
    // Only checking the first 2 elements since we have verified that the last state_type is
    // "cursor_based"
    assertEquals(expectedOrderedColumnValueFromFirstSync.get(0), orderedColumnValuesOfStreamOneFromFirstSync.get(0));
    assertEquals(expectedOrderedColumnValueFromFirstSync.get(1), orderedColumnValuesOfStreamOneFromFirstSync.get(1));
    assertEquals(expectedOrderedColumnValueFromFirstSync.get(0), orderedColumnValuesOfStreamTwoFromFirstSync.get(0));
    assertEquals(expectedOrderedColumnValueFromFirstSync.get(1), orderedColumnValuesOfStreamTwoFromFirstSync.get(1));

    // Extract only state messages for each stream
    final List<AirbyteStateMessage> streamOneStateMessagesFromFirstSync = extractStateMessage(messagesFromFirstSync, streamOneName);
    final List<AirbyteStateMessage> streamTwoStateMessagesFromFirstSync = extractStateMessage(messagesFromFirstSync, streamTwoName);
    // Extract the incremental states of each stream's first and second state message
    final List<JsonNode> streamOneIncrementalStatesFromFirstSync =
        List.of(streamOneStateMessagesFromFirstSync.get(0).getStream().getStreamState().get("incremental_state"),
            streamOneStateMessagesFromFirstSync.get(1).getStream().getStreamState().get("incremental_state"));
    final JsonNode streamOneFinalStreamStateFromFirstSync = streamOneStateMessagesFromFirstSync.get(2).getStream().getStreamState();

    final List<JsonNode> streamTwoIncrementalStatesFromFirstSync =
        List.of(streamTwoStateMessagesFromFirstSync.get(0).getStream().getStreamState().get("incremental_state"),
            streamTwoStateMessagesFromFirstSync.get(1).getStream().getStreamState().get("incremental_state"));
    final JsonNode streamTwoFinalStreamStateFromFirstSync = streamTwoStateMessagesFromFirstSync.get(2).getStream().getStreamState();

    // The incremental_state of each stream's first and second incremental states is expected
    // to be identical to the stream_state of the final state message for each stream
    assertEquals(streamOneIncrementalStatesFromFirstSync.get(0), streamOneFinalStreamStateFromFirstSync);
    assertEquals(streamOneIncrementalStatesFromFirstSync.get(1), streamOneFinalStreamStateFromFirstSync);
    assertEquals(streamTwoIncrementalStatesFromFirstSync.get(0), streamTwoFinalStreamStateFromFirstSync);
    assertEquals(streamTwoIncrementalStatesFromFirstSync.get(1), streamTwoFinalStreamStateFromFirstSync);

    // Sync should work with a ordered_column state AND a cursor-based state from each stream
    // Forcing a sync with
    // - stream one state still being the first record read via Ordered column.
    // - stream two state being the Ordered Column state before the final emitted state before the
    // cursor
    // switch
    final List<AirbyteMessage> messagesFromSecondSyncWithMixedStates = MoreIterators
        .toList(source().read(config, configuredCatalog,
            Jsons.jsonNode(List.of(streamOneStateMessagesFromFirstSync.get(0),
                streamTwoStateMessagesFromFirstSync.get(1)))));

    // Extract only state messages for each stream after second sync
    final List<AirbyteStateMessage> streamOneStateMessagesFromSecondSync =
        extractStateMessage(messagesFromSecondSyncWithMixedStates, streamOneName);
    final List<String> stateTypeOfStreamOneStatesFromSecondSync =
        extractSpecificFieldFromCombinedMessages(messagesFromSecondSyncWithMixedStates, streamOneName, STATE_TYPE_KEY);

    final List<AirbyteStateMessage> streamTwoStateMessagesFromSecondSync =
        extractStateMessage(messagesFromSecondSyncWithMixedStates, streamTwoName);
    final List<String> stateTypeOfStreamTwoStatesFromSecondSync =
        extractSpecificFieldFromCombinedMessages(messagesFromSecondSyncWithMixedStates, streamTwoName, STATE_TYPE_KEY);

    // Stream One states after the second sync are expected to have 2 stream states
    // - 1 with PrimaryKey state_type and 1 state that is of cursorBased state type
    assertEquals(2, streamOneStateMessagesFromSecondSync.size());
    assertEquals(List.of("ordered_column", "cursor_based"), stateTypeOfStreamOneStatesFromSecondSync);

    // Stream Two states after the second sync are expected to have 1 stream state
    // - The state that is of cursorBased state type
    assertEquals(1, streamTwoStateMessagesFromSecondSync.size());
    assertEquals(List.of("cursor_based"), stateTypeOfStreamTwoStatesFromSecondSync);

    // Add some data to each table and perform a third read.
    // Expect to see all records be synced via cursorBased method and not ordered_column
    testdb.with("INSERT INTO %s (id, name, updated_at) VALUES (4,'Hooper','2006-10-19')",
        getFullyQualifiedTableName(streamOneName))
        .with("INSERT INTO %s (id, name, updated_at) VALUES (43, 'Iron Man', '2006-10-19')",
            streamTwoFullyQualifiedName);

    final List<AirbyteMessage> messagesFromThirdSync = MoreIterators
        .toList(source().read(config, configuredCatalog,
            Jsons.jsonNode(List.of(streamOneStateMessagesFromSecondSync.get(1),
                streamTwoStateMessagesFromSecondSync.get(0)))));

    // Extract only state messages, state type, and cursor for each stream after second sync
    final List<AirbyteStateMessage> streamOneStateMessagesFromThirdSync =
        extractStateMessage(messagesFromThirdSync, streamOneName);
    final List<String> stateTypeOfStreamOneStatesFromThirdSync =
        extractSpecificFieldFromCombinedMessages(messagesFromThirdSync, streamOneName, STATE_TYPE_KEY);
    final List<String> cursorOfStreamOneStatesFromThirdSync =
        extractSpecificFieldFromCombinedMessages(messagesFromThirdSync, streamOneName, "cursor");

    final List<AirbyteStateMessage> streamTwoStateMessagesFromThirdSync =
        extractStateMessage(messagesFromThirdSync, streamTwoName);
    final List<String> stateTypeOfStreamTwoStatesFromThirdSync =
        extractSpecificFieldFromCombinedMessages(messagesFromThirdSync, streamTwoName, STATE_TYPE_KEY);
    final List<String> cursorOfStreamTwoStatesFromThirdSync =
        extractSpecificFieldFromCombinedMessages(messagesFromThirdSync, streamTwoName, "cursor");

    // Both streams should now be synced via standard cursor and have updated max cursor values
    // cursor: 4 for stream one
    // cursor: 43 for stream two
    assertEquals(1, streamOneStateMessagesFromThirdSync.size());
    assertEquals(List.of("cursor_based"), stateTypeOfStreamOneStatesFromThirdSync);
    assertEquals(List.of("4"), cursorOfStreamOneStatesFromThirdSync);

    assertEquals(1, streamTwoStateMessagesFromThirdSync.size());
    assertEquals(List.of("cursor_based"), stateTypeOfStreamTwoStatesFromThirdSync);
    assertEquals(List.of("43"), cursorOfStreamTwoStatesFromThirdSync);
  }

  private AirbyteStream getAirbyteStream(final String tableName, final String namespace) {
    return CatalogHelpers.createAirbyteStream(
        tableName,
        namespace,
        Field.of(COL_ID, JsonSchemaType.INTEGER),
        Field.of(COL_NAME, JsonSchemaType.STRING),
        Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
        .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID)));
  }

  @Override
  protected AirbyteCatalog getCatalog(final String defaultNamespace) {
    return new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of(COL_ID))),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_WITHOUT_PK,
            defaultNamespace,
            Field.of(COL_ID, JsonSchemaType.INTEGER),
            Field.of(COL_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(Collections.emptyList()),
        CatalogHelpers.createAirbyteStream(
            TABLE_NAME_COMPOSITE_PK,
            defaultNamespace,
            Field.of(COL_FIRST_NAME, JsonSchemaType.STRING),
            Field.of(COL_LAST_NAME, JsonSchemaType.STRING),
            Field.of(COL_UPDATED_AT, JsonSchemaType.STRING_DATE))
            .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(
                List.of(List.of(COL_FIRST_NAME), List.of(COL_LAST_NAME)))));
  }

  @Override
  protected DbStreamState buildStreamState(final ConfiguredAirbyteStream configuredAirbyteStream,
                                           final String cursorField,
                                           final String cursorValue) {
    return new CursorBasedStatus().withStateType(StateType.CURSOR_BASED).withVersion(2L)
        .withStreamName(configuredAirbyteStream.getStream().getName())
        .withStreamNamespace(configuredAirbyteStream.getStream().getNamespace())
        .withCursorField(List.of(cursorField))
        .withCursor(cursorValue)
        .withCursorRecordCount(1L);
  }

  // Override from parent class as we're no longer including the legacy Data field.
  @Override
  protected List<AirbyteMessage> createExpectedTestMessages(final List<? extends DbStreamState> states, final long numRecords) {
    return states.stream()
        .map(s -> new AirbyteMessage().withType(Type.STATE)
            .withState(
                new AirbyteStateMessage().withType(AirbyteStateType.STREAM)
                    .withStream(new AirbyteStreamState()
                        .withStreamDescriptor(new StreamDescriptor().withNamespace(s.getStreamNamespace()).withName(s.getStreamName()))
                        .withStreamState(Jsons.jsonNode(s)))
                    .withSourceStats(new AirbyteStateStats().withRecordCount((double) numRecords))))
        .collect(
            Collectors.toList());
  }

  @Override
  protected JsonNode getStateData(final AirbyteMessage airbyteMessage, final String streamName) {
    final JsonNode streamState = airbyteMessage.getState().getStream().getStreamState();
    if (streamState.get("stream_name").asText().equals(streamName)) {
      return streamState;
    }

    throw new IllegalArgumentException("Stream not found in state message: " + streamName);
  }

  @Override
  protected List<AirbyteMessage> getExpectedAirbyteMessagesSecondSync(final String namespace) {
    final List<AirbyteMessage> expectedMessages = new ArrayList<>();
    expectedMessages.addAll(List.of(createRecord(streamName(), namespace, ImmutableMap
        .of(COL_ID, ID_VALUE_4,
            COL_NAME, "riker",
            COL_UPDATED_AT, "2006-10-19")),
        createRecord(streamName(), namespace, ImmutableMap
            .of(COL_ID, ID_VALUE_5,
                COL_NAME, "data",
                COL_UPDATED_AT, "2006-10-19"))));
    final DbStreamState state = new CursorBasedStatus()
        .withStateType(StateType.CURSOR_BASED)
        .withVersion(2L)
        .withStreamName(streamName())
        .withStreamNamespace(namespace)
        .withCursorField(ImmutableList.of(COL_ID))
        .withCursor("5")
        .withCursorRecordCount(1L);

    expectedMessages.addAll(createExpectedTestMessages(List.of(state), 2L));
    return expectedMessages;
  }

  @Override
  protected void validateFullRefreshStateMessageReadSuccess(final List<? extends AirbyteStateMessage> stateMessages) {
    var finalStateMessage = stateMessages.get(stateMessages.size() - 1);
    assertEquals(
        finalStateMessage.getStream().getStreamState().get("state_type").textValue(),
        "ordered_column");
    assertEquals(finalStateMessage.getStream().getStreamState().get("ordered_col").textValue(), "id");
    assertEquals(finalStateMessage.getStream().getStreamState().get("ordered_col_val").textValue(), "3");
  }

}
