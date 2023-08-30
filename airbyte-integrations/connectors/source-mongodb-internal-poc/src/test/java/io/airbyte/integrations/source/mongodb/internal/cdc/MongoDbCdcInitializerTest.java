/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import com.mongodb.connection.ClusterDescription;
import com.mongodb.connection.ClusterType;
import com.mongodb.connection.ServerDescription;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumStateUtil;
import io.airbyte.integrations.source.mongodb.internal.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStreamState;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.OptionalLong;
import org.bson.BsonDocument;
import org.bson.BsonString;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MongoDbCdcInitializerTest {

  private static final String COLLECTION = "test-collection";
  private static final String DATABASE = "test-database";
  private static final String ID = "64c0029d95ad260d69ef28a0";
  private static final String REPLICA_SET = "test-replica-set";
  private static final String RESUME_TOKEN1 = "8264BEB9F3000000012B0229296E04";
  private static final String RESUME_TOKEN_AFTER_RESUME_TOKEN1 = "8264BEC9F3000000012B0229296E04";
  private static final String STREAM_NAME = COLLECTION;
  private static final String STREAM_NAMESPACE = DATABASE;

  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          COLLECTION,
          DATABASE,
          Field.of("id", JsonSchemaType.INTEGER),
          Field.of("string", JsonSchemaType.STRING))
          .withSupportedSyncModes(List.of(SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("_id")))));
  protected static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = toConfiguredCatalog(CATALOG);

  final JsonNode CONFIG = Jsons.jsonNode(Map.of(
      MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://host:12345/",
      MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY, DATABASE,
      MongoDbDebeziumConstants.Configuration.REPLICA_SET_CONFIGURATION_KEY, REPLICA_SET));

  final Instant EMITTED_AT = Instant.now();

  private MongoDbCdcInitializer cdcInitializer;
  private MongoDbDebeziumStateUtil mongoDbDebeziumStateUtil;
  private MongoClient mongoClient;
  private MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor;

  @BeforeEach
  void setUp() {
    final BsonDocument resumeTokenDocument = new BsonDocument("_data", new BsonString(RESUME_TOKEN1));

    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final MongoCollection mongoCollection = mock(MongoCollection.class);
    final FindIterable<BsonDocument> findIterable = mock(FindIterable.class);
    final MongoCursor<BsonDocument> cursor = mock(MongoCursor.class);
    final ServerDescription serverDescription = mock(ServerDescription.class);
    final ClusterDescription clusterDescription = mock(ClusterDescription.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(serverDescription.getSetName()).thenReturn(REPLICA_SET);
    when(clusterDescription.getServerDescriptions()).thenReturn(List.of(serverDescription));
    when(clusterDescription.getType()).thenReturn(ClusterType.REPLICA_SET);
    when(mongoClient.watch(BsonDocument.class)).thenReturn(changeStreamIterable);
    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);
    when(mongoClient.getClusterDescription()).thenReturn(clusterDescription);
    when(mongoDatabase.getCollection(COLLECTION)).thenReturn(mongoCollection);
    when(mongoCollection.find()).thenReturn(findIterable);
    when(findIterable.filter(any())).thenReturn(findIterable);
    when(findIterable.projection(any())).thenReturn(findIterable);
    when(findIterable.sort(any())).thenReturn(findIterable);
    when(findIterable.cursor()).thenReturn(cursor);

    mongoDbDebeziumStateUtil = spy(new MongoDbDebeziumStateUtil());
    cdcInitializer = new MongoDbCdcInitializer(mongoDbDebeziumStateUtil);
  }

  @Test
  void testCreateCdcIteratorsEmptyInitialState() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, CONFIGURED_CATALOG, stateManager, EMITTED_AT, CONFIG);
    assertNotNull(iterators);
    assertEquals(2, iterators.size(), "Should have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
  }

  @Test
  void testCreateCdcIteratorsFromInitialStateWithInProgressInitialSnapshot() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(createInitialDebeziumState(InitialSnapshotStatus.IN_PROGRESS));
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, CONFIGURED_CATALOG, stateManager, EMITTED_AT, CONFIG);
    assertNotNull(iterators);
    assertEquals(2, iterators.size(), "Should have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
  }

  @Test
  void testCreateCdcIteratorsFromInitialStateWithCompletedInitialSnapshot() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(createInitialDebeziumState(InitialSnapshotStatus.COMPLETE));
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, CONFIGURED_CATALOG, stateManager, EMITTED_AT, CONFIG);
    assertNotNull(iterators);
    assertEquals(1, iterators.size(), "Should only have 1 iterator for the cdc stream since initial snapshot has been completed");
  }

  @Test
  void testCreateCdcIteratorsWithCompletedInitialSnapshotSavedOffsetBeforeResumeToken() {
    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(new BsonDocument("_data", new BsonString(RESUME_TOKEN_AFTER_RESUME_TOKEN1)));
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(createInitialDebeziumState(InitialSnapshotStatus.COMPLETE));
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, CONFIGURED_CATALOG, stateManager, EMITTED_AT, CONFIG);
    assertNotNull(iterators);
    assertEquals(2, iterators.size(), "Should have two iterators since a full refresh is required due to saved offset being before most recent resume token");
  }

  @Test
  void testUnableToExtractOffsetFromStateException() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(createInitialDebeziumState(InitialSnapshotStatus.COMPLETE));
    doReturn(OptionalLong.empty()).when(mongoDbDebeziumStateUtil).savedOffset(any(), any(), any(), any(), any());
    assertThrows(RuntimeException.class, () -> cdcInitializer.createCdcIterators(mongoClient, CONFIGURED_CATALOG, stateManager, EMITTED_AT, CONFIG));
  }

  private static JsonNode createInitialDebeziumState(final InitialSnapshotStatus initialSnapshotStatus) {
    final StreamDescriptor streamDescriptor = new StreamDescriptor().withNamespace(STREAM_NAMESPACE).withName(STREAM_NAME);
    final MongoDbCdcState cdcState = new MongoDbCdcState(MongoDbDebeziumStateUtil.formatState(DATABASE, REPLICA_SET, RESUME_TOKEN1));
    final MongoDbStreamState mongoDbStreamState = new MongoDbStreamState(ID, initialSnapshotStatus);
    final JsonNode sharedState = Jsons.jsonNode(cdcState);
    final JsonNode streamState = Jsons.jsonNode(mongoDbStreamState);
    final AirbyteStreamState airbyteStreamState = new AirbyteStreamState().withStreamDescriptor(streamDescriptor).withStreamState(streamState);
    final AirbyteGlobalState airbyteGlobalState = new AirbyteGlobalState().withSharedState(sharedState).withStreamStates(List.of(airbyteStreamState));
    final AirbyteStateMessage airbyteStateMessage =
        new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.GLOBAL).withGlobal(airbyteGlobalState);
    return Jsons.jsonNode(List.of(airbyteStateMessage));
  }

  public static ConfiguredAirbyteCatalog toConfiguredCatalog(final AirbyteCatalog catalog) {
    return (new ConfiguredAirbyteCatalog()).withStreams(catalog.getStreams().stream().map(MongoDbCdcInitializerTest::toConfiguredStream).toList());
  }

  public static ConfiguredAirbyteStream toConfiguredStream(final AirbyteStream stream) {
    return (new ConfiguredAirbyteStream())
        .withStream(stream)
        .withSyncMode(SyncMode.INCREMENTAL)
        .withCursorField(new ArrayList<>())
        .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
        .withPrimaryKey(new ArrayList<>());
  }
}
