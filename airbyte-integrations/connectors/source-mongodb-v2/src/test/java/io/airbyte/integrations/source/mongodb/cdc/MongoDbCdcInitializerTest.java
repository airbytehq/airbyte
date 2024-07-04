/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIG_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.INVALID_CDC_CURSOR_POSITION_PROPERTY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.RESYNC_DATA_OPTION;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.Mockito.doCallRealMethod;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.MongoCommandException;
import com.mongodb.ServerAddress;
import com.mongodb.client.AggregateIterable;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import com.mongodb.connection.ClusterDescription;
import com.mongodb.connection.ClusterType;
import com.mongodb.connection.ServerDescription;
import io.airbyte.cdk.integrations.source.relationaldb.streamstatus.StreamStatusTraceEmitterIterator;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.source.mongodb.MongoDbSourceConfig;
import io.airbyte.integrations.source.mongodb.state.IdType;
import io.airbyte.integrations.source.mongodb.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
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
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Consumer;
import org.bson.BsonDocument;
import org.bson.BsonString;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MongoDbCdcInitializerTest {

  private static final String COLLECTION = "test-collection";
  private static final String DATABASE = "test-database";
  private static final String ID = "64c0029d95ad260d69ef28a0";
  private static final String REPLICA_SET = "test-replica-set";
  private static final String RESUME_TOKEN1 = "8264BEB9F3000000012B0229296E04";
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
  protected static final List<ConfiguredAirbyteStream> CONFIGURED_CATALOG_STREAMS = CONFIGURED_CATALOG.getStreams();
  final MongoDbSourceConfig CONFIG = new MongoDbSourceConfig(Jsons.jsonNode(
      Map.of(DATABASE_CONFIG_CONFIGURATION_KEY,
          Map.of(
              MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://host:12345/",
              MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY, DATABASE))));

  final Instant EMITTED_AT = Instant.now();

  private MongoDbCdcInitializer cdcInitializer;
  private MongoDbDebeziumStateUtil mongoDbDebeziumStateUtil;
  private MongoClient mongoClient;
  private MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor;
  private AggregateIterable<Document> aggregateIterable;
  private MongoCursor<Document> aggregateCursor;
  private MongoCursor<Document> findCursor;
  private ChangeStreamIterable<BsonDocument> changeStreamIterable;
  private MongoDbCdcConnectorMetadataInjector cdcConnectorMetadataInjector;
  private static final List<Bson> PIPELINE = Collections.singletonList(Aggregates.match(
      Filters.in("ns.coll", List.of(COLLECTION))));

  @BeforeEach
  void setUp() {
    final BsonDocument resumeTokenDocument = new BsonDocument("_data", new BsonString(RESUME_TOKEN1));
    final Document aggregate = Document.parse("{\"_id\": {\"_id\": \"objectId\"}, \"count\": 1}");

    changeStreamIterable = mock(ChangeStreamIterable.class);
    mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final MongoCollection mongoCollection = mock(MongoCollection.class);
    final FindIterable<Document> findIterable = mock(FindIterable.class);
    findCursor = mock(MongoCursor.class);
    final ServerDescription serverDescription = mock(ServerDescription.class);
    final ClusterDescription clusterDescription = mock(ClusterDescription.class);
    aggregateIterable = mock(AggregateIterable.class);
    aggregateCursor = mock(MongoCursor.class);
    cdcConnectorMetadataInjector = mock(MongoDbCdcConnectorMetadataInjector.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(serverDescription.getSetName()).thenReturn(REPLICA_SET);
    when(clusterDescription.getServerDescriptions()).thenReturn(List.of(serverDescription));
    when(clusterDescription.getType()).thenReturn(ClusterType.REPLICA_SET);
    when(mongoClient.watch(BsonDocument.class)).thenReturn(changeStreamIterable);
    when(mongoDatabase.watch(PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);
    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);
    when(mongoClient.getClusterDescription()).thenReturn(clusterDescription);
    when(mongoDatabase.getCollection(COLLECTION)).thenReturn(mongoCollection);
    when(mongoCollection.aggregate(anyList())).thenReturn(aggregateIterable);
    when(aggregateIterable.iterator()).thenReturn(aggregateCursor);
    when(aggregateCursor.hasNext()).thenReturn(true, false);
    when(aggregateCursor.next()).thenReturn(aggregate);
    doCallRealMethod().when(aggregateIterable).forEach(any(Consumer.class));
    when(mongoCollection.find()).thenReturn(findIterable);
    when(findIterable.filter(any())).thenReturn(findIterable);
    when(findIterable.projection(any())).thenReturn(findIterable);
    when(findIterable.limit(anyInt())).thenReturn(findIterable);
    when(findIterable.sort(any())).thenReturn(findIterable);
    when(findIterable.cursor()).thenReturn(findCursor);
    when(findCursor.hasNext()).thenReturn(true);
    when(findCursor.next()).thenReturn(new Document("_id", new ObjectId(ID)));
    when(findIterable.allowDiskUse(anyBoolean())).thenReturn(findIterable);

    mongoDbDebeziumStateUtil = spy(new MongoDbDebeziumStateUtil());
    cdcInitializer = new MongoDbCdcInitializer(mongoDbDebeziumStateUtil);
  }

  @Test
  void testCreateCdcIteratorsEmptyInitialState() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null, CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT, CONFIG);
    assertNotNull(iterators);
    assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
    assertTrue(iterators.get(0).hasNext(),
        "Initial snapshot iterator should at least have one message if there's no initial snapshot state and collections are not empty");
  }

  @Test
  void testCreateCdcIteratorsEmptyInitialStateEmptyCollections() {
    when(findCursor.hasNext()).thenReturn(false);
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null, CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT, CONFIG);
    assertNotNull(iterators);
    assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
  }

  @Test
  void testCreateCdcIteratorsFromInitialStateWithInProgressInitialSnapshot() {
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumState(InitialSnapshotStatus.IN_PROGRESS), CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT, CONFIG);
    assertNotNull(iterators);
    assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
    assertTrue(iterators.get(0).hasNext(),
        "Initial snapshot iterator should at least have one message if the initial snapshot state is set as in progress");
  }

  @Test
  void testCreateCdcIteratorsFromInitialStateWithCompletedInitialSnapshot() {
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumState(InitialSnapshotStatus.COMPLETE), CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT, CONFIG);
    assertNotNull(iterators);
    assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
    assertFalse(iterators.get(0).hasNext(), "Initial snapshot iterator should have no messages if its snapshot state is set as complete");
  }

  @Test
  void testCreateCdcIteratorsWithCompletedInitialSnapshotSavedOffsetInvalidDefaultBehavior() {
    when(changeStreamIterable.cursor())
        .thenReturn(mongoChangeStreamCursor)
        .thenThrow(new MongoCommandException(new BsonDocument(), new ServerAddress()))
        .thenReturn(mongoChangeStreamCursor);
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumState(InitialSnapshotStatus.COMPLETE), CONFIG);
    assertThrows(ConfigErrorException.class,
        () -> cdcInitializer.createCdcIterators(mongoClient, cdcConnectorMetadataInjector, CONFIGURED_CATALOG_STREAMS,
            stateManager, EMITTED_AT, CONFIG));
  }

  @Test
  void testCreateCdcIteratorsWithCompletedInitialSnapshotSavedOffsetFailOption() {
    when(changeStreamIterable.cursor())
        .thenReturn(mongoChangeStreamCursor)
        .thenThrow(new MongoCommandException(new BsonDocument(), new ServerAddress()))
        .thenReturn(mongoChangeStreamCursor);
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumState(InitialSnapshotStatus.COMPLETE), CONFIG);
    assertThrows(ConfigErrorException.class,
        () -> cdcInitializer.createCdcIterators(mongoClient, cdcConnectorMetadataInjector, CONFIGURED_CATALOG_STREAMS,
            stateManager, EMITTED_AT, CONFIG));
  }

  @Test
  void testCreateCdcIteratorsWithCompletedInitialSnapshotSavedOffsetInvalidResyncOption() {
    MongoDbSourceConfig resyncConfig = new MongoDbSourceConfig(createConfig(RESYNC_DATA_OPTION));
    when(changeStreamIterable.cursor())
        .thenReturn(mongoChangeStreamCursor)
        .thenThrow(new MongoCommandException(new BsonDocument(), new ServerAddress()))
        .thenReturn(mongoChangeStreamCursor);
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumState(InitialSnapshotStatus.COMPLETE), CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT, resyncConfig);
    assertNotNull(iterators);
    assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
    assertTrue(iterators.get(0).hasNext(),
        "Initial snapshot iterator should at least have one message if its snapshot state is set as complete but needs to start over due to invalid saved offset");
  }

  JsonNode createConfig(String cdcCursorFailBehaviour) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(DATABASE_CONFIG_CONFIGURATION_KEY,
            Map.of(
                MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://host:12345/",
                MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY, DATABASE))
        .put(INVALID_CDC_CURSOR_POSITION_PROPERTY, cdcCursorFailBehaviour)
        .build());
  }

  @Test
  void testUnableToExtractOffsetFromStateException() {
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumState(InitialSnapshotStatus.COMPLETE), CONFIG);
    doReturn(Optional.empty()).when(mongoDbDebeziumStateUtil).savedOffset(any(), any(), any(), any());
    assertThrows(RuntimeException.class,
        () -> cdcInitializer.createCdcIterators(mongoClient, cdcConnectorMetadataInjector, CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT,
            CONFIG));
  }

  @Test
  void testMultipleIdTypesThrowsException() {
    final Document aggregate1 = Document.parse("{\"_id\": {\"_id\": \"objectId\"}, \"count\": 1}");
    final Document aggregate2 = Document.parse("{\"_id\": {\"_id\": \"string\"}, \"count\": 1}");

    when(aggregateCursor.hasNext()).thenReturn(true, true, false);
    when(aggregateCursor.next()).thenReturn(aggregate1, aggregate2);
    doCallRealMethod().when(aggregateIterable).forEach(any(Consumer.class));

    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumState(InitialSnapshotStatus.IN_PROGRESS), CONFIG);

    final var thrown = assertThrows(ConfigErrorException.class, () -> cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT, CONFIG));
    assertTrue(thrown.getMessage().contains("must be consistently typed"));
  }

  @Test
  void testUnsupportedIdTypeThrowsException() {
    final Document aggregate = Document.parse("{\"_id\": {\"_id\": \"exotic\"}, \"count\": 1}");

    when(aggregateCursor.hasNext()).thenReturn(true, false);
    when(aggregateCursor.next()).thenReturn(aggregate);
    doCallRealMethod().when(aggregateIterable).forEach(any(Consumer.class));

    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null, CONFIG);

    final var thrown = assertThrows(ConfigErrorException.class, () -> cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT, CONFIG));
    assertTrue(thrown.getMessage().contains("_id fields with the following types are currently supported"));
  }

  private static JsonNode createInitialDebeziumState(final InitialSnapshotStatus initialSnapshotStatus) {
    final StreamDescriptor streamDescriptor = new StreamDescriptor().withNamespace(STREAM_NAMESPACE).withName(STREAM_NAME);
    final MongoDbCdcState cdcState = new MongoDbCdcState(MongoDbDebeziumStateUtil.formatState(DATABASE, RESUME_TOKEN1));
    final MongoDbStreamState mongoDbStreamState = new MongoDbStreamState(ID, initialSnapshotStatus, IdType.OBJECT_ID);
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

  private List<AutoCloseableIterator<AirbyteMessage>> filterTraceIterator(List<AutoCloseableIterator<AirbyteMessage>> iterators) {
    return iterators.stream().filter(it -> it instanceof StreamStatusTraceEmitterIterator == false).toList();
  }

}
