/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.createRecord;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.extractStateMessage;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.filterRecords;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.map;
import static io.airbyte.integrations.source.postgres.utils.PostgresUnitTestsUtil.setEmittedAtToNull;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.source.postgres.PostgresTestDatabase.BaseImage;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateStats;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class XminPostgresSourceTest {

  private static final String SCHEMA_NAME = "public";
  protected static final String STREAM_NAME = "id_and_name";
  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          STREAM_NAME,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING),
          Field.of("power", JsonSchemaType.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedCursor(true)
          .withSourceDefinedPrimaryKey(List.of(List.of("id")))
          .withIsResumable(true),
      CatalogHelpers.createAirbyteStream(
          STREAM_NAME + "2",
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING),
          Field.of("power", JsonSchemaType.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedCursor(true)
          .withIsResumable(true),
      CatalogHelpers.createAirbyteStream(
          "names",
          SCHEMA_NAME,
          Field.of("first_name", JsonSchemaType.STRING),
          Field.of("last_name", JsonSchemaType.STRING),
          Field.of("power", JsonSchemaType.NUMBER))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withSourceDefinedCursor(true)
          .withSourceDefinedPrimaryKey(List.of(List.of("first_name"), List.of("last_name")))
          .withIsResumable(true)));

  protected static final ConfiguredAirbyteCatalog CONFIGURED_XMIN_CATALOG = toConfiguredXminCatalog(CATALOG);

  protected static final List<AirbyteMessage> INITIAL_RECORD_MESSAGES = Arrays.asList(
      createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("1.0"), "name", "goku", "power", null)),
      createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("2.0"), "name", "vegeta", "power", 9000.1)),
      createRecord(STREAM_NAME, SCHEMA_NAME, map("id", null, "name", "piccolo", "power", null)));

  protected static final List<AirbyteMessage> NEXT_RECORD_MESSAGES = Arrays.asList(
      createRecord(STREAM_NAME, SCHEMA_NAME, map("id", new BigDecimal("3.0"), "name", "gohan", "power", 222.1)));

  protected PostgresTestDatabase testdb;

  protected BaseImage getDatabaseImage() {
    return BaseImage.POSTGRES_12;
  }

  @BeforeEach
  protected void setup() {
    testdb = PostgresTestDatabase.in(getDatabaseImage())
        .with("CREATE TABLE id_and_name(id NUMERIC(20, 10) NOT NULL, name VARCHAR(200) NOT NULL, power double precision NOT NULL, PRIMARY KEY (id));")
        .with("CREATE INDEX i1 ON id_and_name (id);")
        .with("INSERT INTO id_and_name (id, name, power) VALUES (1,'goku', 'Infinity'), (2, 'vegeta', 9000.1), ('NaN', 'piccolo', '-Infinity');")
        .with("CREATE TABLE id_and_name2(id NUMERIC(20, 10) NOT NULL, name VARCHAR(200) NOT NULL, power double precision NOT NULL);")
        .with("INSERT INTO id_and_name2 (id, name, power) VALUES (1,'goku', 'Infinity'),  (2, 'vegeta', 9000.1), ('NaN', 'piccolo', '-Infinity');")
        .with(
            "CREATE TABLE names(first_name VARCHAR(200) NOT NULL, last_name VARCHAR(200) NOT NULL, power double precision NOT NULL, PRIMARY KEY (first_name, last_name));")
        .with(
            "INSERT INTO names (first_name, last_name, power) VALUES ('san', 'goku', 'Infinity'),  ('prince', 'vegeta', 9000.1), ('piccolo', 'junior', '-Infinity');");
  }

  @AfterEach
  protected void tearDown() {
    testdb.close();
  }

  protected JsonNode getXminConfig() {
    return testdb.testConfigBuilder()
        .withSchemas(SCHEMA_NAME)
        .withoutSsl()
        .withXminReplication()
        .with(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .build();
  }

  protected Source source() {
    PostgresSource source = new PostgresSource();
    return PostgresSource.sshWrappedSource(source);
  }

  @Test
  void testDiscover() throws Exception {
    final AirbyteCatalog actual = source().discover(getXminConfig());
    actual.getStreams().forEach(actualStream -> {
      final Optional<AirbyteStream> expectedStream =
          CATALOG.getStreams().stream().filter(stream -> stream.getName().equals(actualStream.getName())).findAny();
      assertTrue(expectedStream.isPresent());
      assertEquals(expectedStream.get(), actualStream);
    });
  }

  @Test
  void testDiscoverDisableIncrementalSyncForView() throws Exception {
    testdb.query(ctx -> {
      ctx.fetch("CREATE VIEW id_and_name_view AS SELECT * FROM id_and_name;");
      return null;
    });
    final AirbyteCatalog actual = source().discover(getXminConfig());
    actual.getStreams().forEach(actualStream -> {
      if (actualStream.getName().equals("id_and_name_view")) {
        assertTrue(!actualStream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL));
        assertTrue(actualStream.getSupportedSyncModes().contains(SyncMode.FULL_REFRESH));
      }
    });
    testdb.query(ctx -> {
      ctx.fetch("DROP VIEW id_and_name_view;");
      return null;
    });
  }

  @Test
  void testReadSuccess() throws Exception {
    // Perform an initial sync with the configured catalog, which is set up to use xmin_replication.
    // All of the records in the configured stream should be emitted.
    final ConfiguredAirbyteCatalog configuredCatalog =
        CONFIGURED_XMIN_CATALOG
            .withStreams(CONFIGURED_XMIN_CATALOG.getStreams().stream().filter(s -> s.getStream().getName().equals(STREAM_NAME)).collect(
                Collectors.toList()));
    final List<AirbyteMessage> recordsFromFirstSync =
        MoreIterators.toList(source().read(getXminConfig(), configuredCatalog, null));
    setEmittedAtToNull(recordsFromFirstSync);
    assertThat(filterRecords(recordsFromFirstSync)).containsExactlyElementsOf(INITIAL_RECORD_MESSAGES);

    // Extract the state message and assert that it exists. It contains the xmin value, so validating
    // the actual value isn't useful right now.
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessage(recordsFromFirstSync);
    // We should have 3 state messages because we have set state emission frequency after each record in
    // the test
    assertEquals(3, stateAfterFirstBatch.size());

    final AirbyteStateMessage firstStateMessage = stateAfterFirstBatch.get(0);
    final String stateTypeFromFirstStateMessage = firstStateMessage.getStream().getStreamState().get("state_type").asText();
    final String ctidFromFirstStateMessage = firstStateMessage.getStream().getStreamState().get("ctid").asText();
    final JsonNode incrementalStateFromFirstStateMessage = firstStateMessage.getStream().getStreamState().get("incremental_state");

    final AirbyteStateMessage secondStateMessage = stateAfterFirstBatch.get(1);
    final String stateTypeFromSecondStateMessage = secondStateMessage.getStream().getStreamState().get("state_type").asText();
    final String ctidFromSecondStateMessage = secondStateMessage.getStream().getStreamState().get("ctid").asText();
    final JsonNode incrementalStateFromSecondStateMessage = secondStateMessage.getStream().getStreamState().get("incremental_state");

    final AirbyteStateMessage thirdStateMessage = stateAfterFirstBatch.get(2);
    final String stateTypeFromThirdStateMessage = thirdStateMessage.getStream().getStreamState().get("state_type").asText();

    // First two state messages should be of ctid type
    assertEquals("ctid", stateTypeFromFirstStateMessage);
    assertEquals("ctid", stateTypeFromSecondStateMessage);

    // Since the third state message would be the final, it should be of xmin type
    assertEquals("xmin", stateTypeFromThirdStateMessage);

    assertEquals(firstStateMessage.getSourceStats().getRecordCount(), 1.0);
    assertEquals(secondStateMessage.getSourceStats().getRecordCount(), 1.0);
    assertEquals(thirdStateMessage.getSourceStats().getRecordCount(), 1.0);

    // The ctid value from second state message should be bigger than first state message
    assertEquals(1, ctidFromSecondStateMessage.compareTo(ctidFromFirstStateMessage));

    // The incremental state value from first and second state message should be the same
    assertNotNull(incrementalStateFromFirstStateMessage);
    assertNotNull(incrementalStateFromSecondStateMessage);
    assertEquals(incrementalStateFromFirstStateMessage, incrementalStateFromSecondStateMessage);

    // The third state message should be equal to incremental_state of first two state messages
    assertEquals(incrementalStateFromFirstStateMessage, thirdStateMessage.getStream().getStreamState());

    // Assert that the last message in the sequence is a state message
    assertMessageSequence(recordsFromFirstSync);

    // Sync should work with a ctid state
    final List<AirbyteMessage> recordsFromSyncRunningWithACtidState =
        MoreIterators.toList(source().read(getXminConfig(), configuredCatalog,
            Jsons.jsonNode(Collections.singletonList(firstStateMessage))));
    setEmittedAtToNull(recordsFromSyncRunningWithACtidState);
    final List<AirbyteMessage> expectedDataFromSyncUsingFirstCtidState = new ArrayList<>(2);
    final AtomicBoolean skippedFirstRecord = new AtomicBoolean(false);
    INITIAL_RECORD_MESSAGES.forEach(c -> {
      if (!skippedFirstRecord.get()) {
        skippedFirstRecord.set(true);
        return;
      }
      expectedDataFromSyncUsingFirstCtidState.add(c);
    });
    assertThat(filterRecords(recordsFromSyncRunningWithACtidState)).containsExactlyElementsOf(expectedDataFromSyncUsingFirstCtidState);

    final List<AirbyteStateMessage> stateAfterSyncWithCtidState = extractStateMessage(recordsFromSyncRunningWithACtidState);
    // Since only 2 records should be emitted so 2 state messages are expected
    assertEquals(2, stateAfterSyncWithCtidState.size());
    assertEquals(secondStateMessage, stateAfterSyncWithCtidState.get(0));
    assertEquals(thirdStateMessage, stateAfterSyncWithCtidState.get(1));
    assertEquals(stateAfterSyncWithCtidState.get(0).getSourceStats().getRecordCount(), 1.0);
    assertEquals(stateAfterSyncWithCtidState.get(1).getSourceStats().getRecordCount(), 1.0);

    assertMessageSequence(recordsFromSyncRunningWithACtidState);

    // Read with the final xmin state message should return no data
    final List<AirbyteMessage> syncWithXminStateType =
        MoreIterators.toList(source().read(getXminConfig(), configuredCatalog,
            Jsons.jsonNode(Collections.singletonList(thirdStateMessage))));
    setEmittedAtToNull(syncWithXminStateType);
    assertEquals(0, filterRecords(syncWithXminStateType).size());

    // Even though no records were emitted, a state message is still expected
    final List<AirbyteStateMessage> stateAfterXminSync = extractStateMessage(syncWithXminStateType);
    assertEquals(1, stateAfterXminSync.size());
    // Since no records were returned so the state should be the same as before without the count.
    thirdStateMessage.setSourceStats(new AirbyteStateStats().withRecordCount(0.0));
    assertEquals(thirdStateMessage, stateAfterXminSync.get(0));

    // We add some data and perform a third read. We should verify that (i) a delete is not captured and
    // (ii) the new record that is inserted into the
    // table is read.
    testdb.query(ctx -> {
      ctx.fetch("DELETE FROM id_and_name WHERE id = 'NaN';");
      ctx.fetch("INSERT INTO id_and_name (id, name, power) VALUES (3, 'gohan', 222.1);");
      return null;
    });

    final List<AirbyteMessage> recordsAfterLastSync =
        MoreIterators.toList(source().read(getXminConfig(), configuredCatalog,
            Jsons.jsonNode(Collections.singletonList(stateAfterXminSync.get(0)))));
    setEmittedAtToNull(recordsAfterLastSync);
    assertThat(filterRecords(recordsAfterLastSync)).containsExactlyElementsOf(NEXT_RECORD_MESSAGES);
    assertMessageSequence(recordsAfterLastSync);
    final List<AirbyteStateMessage> stateAfterLastSync = extractStateMessage(recordsAfterLastSync);
    assertEquals(1, stateAfterLastSync.size());

    final AirbyteStateMessage finalStateMesssage = stateAfterLastSync.get(0);
    final String stateTypeFromFinalStateMessage = finalStateMesssage.getStream().getStreamState().get("state_type").asText();
    assertEquals("xmin", stateTypeFromFinalStateMessage);
    assertTrue(finalStateMesssage.getStream().getStreamState().get("xmin_xid_value").asLong() > thirdStateMessage.getStream().getStreamState()
        .get("xmin_xid_value").asLong());
    assertTrue(finalStateMesssage.getStream().getStreamState().get("xmin_raw_value").asLong() > thirdStateMessage.getStream().getStreamState()
        .get("xmin_raw_value").asLong());
  }

  // Assert that the trace message is the last message to be emitted.
  protected static void assertMessageSequence(final List<AirbyteMessage> messages) {
    assertEquals(Type.TRACE, messages.get(messages.size() - 1).getType());
    assertEquals(Type.STATE, messages.get(messages.size() - 2).getType());
  }

  private static ConfiguredAirbyteCatalog toConfiguredXminCatalog(final AirbyteCatalog catalog) {
    return new ConfiguredAirbyteCatalog()
        .withStreams(catalog.getStreams()
            .stream()
            .map(s -> toConfiguredIncrementalStream(s))
            .toList());
  }

  private static ConfiguredAirbyteStream toConfiguredIncrementalStream(final AirbyteStream stream) {
    return new ConfiguredAirbyteStream()
        .withStream(stream)
        .withSyncMode(SyncMode.INCREMENTAL)
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withPrimaryKey(List.of(List.of("id")));
  }

}
