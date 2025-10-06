/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIG_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.INVALID_CDC_CURSOR_POSITION_PROPERTY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.RESYNC_DATA_OPTION;
import static org.junit.jupiter.api.Assertions.assertEquals;
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
import io.debezium.connector.mongodb.ResumeTokens;
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
  private static final String COLLECTION_1 = "test-collection-1";
  private static final String DATABASE = "test-database";
  private static final String DATABASE_1 = "test-database-1"; // multiple dbs
  private static final String ID = "64c0029d95ad260d69ef28a0";
  private static final String REPLICA_SET = "test-replica-set";
  private static final String RESUME_TOKEN1 = "8264BEB9F3000000012B0229296E04";
  private static final String STREAM_NAME = COLLECTION;
  private static final String STREAM_NAME_1 = COLLECTION_1;
  private static final String STREAM_NAMESPACE = DATABASE;
  private static final String STREAM_NAMESPACE_1 = DATABASE_1;
  private static final String RESUME_TOKEN = "8264BEB9F3000000012B0229296E04";

  private static final AirbyteCatalog SINGLE_DB_CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          COLLECTION,
          DATABASE,
          Field.of("id", JsonSchemaType.INTEGER),
          Field.of("string", JsonSchemaType.STRING))
          .withSupportedSyncModes(List.of(SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("_id")))));

  protected static final ConfiguredAirbyteCatalog SINGLE_DB_CONFIGURED_CATALOG = toConfiguredCatalog(SINGLE_DB_CATALOG);
  protected static final List<ConfiguredAirbyteStream> SINGLE_DB_CONFIGURED_CATALOG_STREAMS = SINGLE_DB_CONFIGURED_CATALOG.getStreams();

  private static final AirbyteCatalog MULTIPLE_DB_CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          "test-collection",
          DATABASE,
          Field.of("id", JsonSchemaType.INTEGER),
          Field.of("string", JsonSchemaType.STRING))
          .withSupportedSyncModes(List.of(SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("_id"))),
      CatalogHelpers.createAirbyteStream(
          "test-collection-1",
          DATABASE_1,
          Field.of("id", JsonSchemaType.INTEGER),
          Field.of("name", JsonSchemaType.STRING))
          .withSupportedSyncModes(List.of(SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("_id")))));

  // List<ConfiguredAirbyteStream> database1Streams =
  // CatalogHelpers.toDefaultConfiguredCatalog(MULTIPLE_DB_CATALOG).getStreams()
  // .stream().filter(stream -> stream.getStream().getNamespace().equals(DATABASE))
  // .toList();
  //
  // List<ConfiguredAirbyteStream> database2Streams =
  // CatalogHelpers.toDefaultConfiguredCatalog(MULTIPLE_DB_CATALOG).getStreams().stream()
  // .filter(stream -> stream.getStream().getNamespace().equals(DATABASE_1))
  // .toList();

  // protected static final List<ConfiguredAirbyteStream> MULTIPLE_DB_CONFIGURED_CATALOG_STREAMS =
  // SINGLE_DB_CONFIGURED_CATALOG.getStreams();

  protected static final ConfiguredAirbyteCatalog MULTIPLE_DB_CONFIGURED_CATALOG = toConfiguredCatalog(MULTIPLE_DB_CATALOG);
  protected static final List<ConfiguredAirbyteStream> MULTIPLE_DB_CONFIGURED_CATALOG_STREAMS = MULTIPLE_DB_CONFIGURED_CATALOG.getStreams();

  final List<Bson> SINGLE_DB_PIPELINE = Collections.singletonList(Aggregates.match(
      Filters.or(List.of(
          Filters.and(
              Filters.eq("ns.db", DATABASE),
              Filters.in("ns.coll", List.of("test-collection")))))));

  private static final List<Bson> MULTIPLE_DB_PIPELINE = Collections.singletonList(Aggregates.match(
      Filters.or(List.of(
          Filters.and(
              Filters.eq("ns.db", DATABASE),
              Filters.in("ns.coll", List.of("test-collection"))),
          Filters.and(
              Filters.eq("ns.db", DATABASE_1),
              Filters.in("ns.coll", List.of("test-collection-1")))))));

  final MongoDbSourceConfig SINGLE_DB_CONFIG = new MongoDbSourceConfig(Jsons.jsonNode(
      Map.of(DATABASE_CONFIG_CONFIGURATION_KEY,
          Map.of(
              MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://host:12345/",
              MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY, List.of(DATABASE)))));

  final MongoDbSourceConfig MULTIPLE_DB_CONFIG = new MongoDbSourceConfig(Jsons.jsonNode(
      Map.of(DATABASE_CONFIG_CONFIGURATION_KEY,
          Map.of(
              MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://host:12345/",
              MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY, List.of(DATABASE, DATABASE_1)))));

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

  @BeforeEach
  void setUp() {
    // Common setup for all tests
    final BsonDocument resumeTokenDocument = new BsonDocument("_data", new BsonString(RESUME_TOKEN1));
    final Document aggregate = Document.parse("{\"_id\": {\"_id\": \"objectId\"}, \"count\": 1}");

    changeStreamIterable = mock(ChangeStreamIterable.class);
    mongoChangeStreamCursor = mock(MongoChangeStreamCursor.class);
    mongoClient = mock(MongoClient.class);
    findCursor = mock(MongoCursor.class);
    final ServerDescription serverDescription = mock(ServerDescription.class);
    final ClusterDescription clusterDescription = mock(ClusterDescription.class);
    aggregateIterable = mock(AggregateIterable.class);
    aggregateCursor = mock(MongoCursor.class);
    cdcConnectorMetadataInjector = mock(MongoDbCdcConnectorMetadataInjector.class);

    // Common mocking
    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);

    when(serverDescription.getSetName()).thenReturn(REPLICA_SET);
    when(clusterDescription.getServerDescriptions()).thenReturn(List.of(serverDescription));
    when(clusterDescription.getType()).thenReturn(ClusterType.REPLICA_SET);
    when(mongoClient.getClusterDescription()).thenReturn(clusterDescription);

    // Aggregate and find mocking
    when(aggregateIterable.iterator()).thenReturn(aggregateCursor);
    when(aggregateCursor.hasNext()).thenReturn(true, false);
    when(aggregateCursor.next()).thenReturn(aggregate);
    doCallRealMethod().when(aggregateIterable).forEach(any(Consumer.class));
    when(findCursor.hasNext()).thenReturn(true);
    when(findCursor.next()).thenReturn(new Document("_id", new ObjectId(ID)));

    mongoDbDebeziumStateUtil = spy(new MongoDbDebeziumStateUtil());
    cdcInitializer = new MongoDbCdcInitializer(mongoDbDebeziumStateUtil);
  }

  private void setupSingleDatabase() {
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final MongoCollection mongoCollection = mock(MongoCollection.class);
    final FindIterable<Document> findIterable = mock(FindIterable.class);
    final BsonDocument resumeToken = ResumeTokens.fromData(RESUME_TOKEN);

    // Mock the single database setup
    when(mongoClient.watch(BsonDocument.class)).thenReturn(changeStreamIterable);
    when(mongoClient.watch(SINGLE_DB_PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);

    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);
    when(mongoDatabase.watch(SINGLE_DB_PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);
    when(mongoDatabase.getCollection(COLLECTION)).thenReturn(mongoCollection);
    when(mongoDatabase.getName()).thenReturn(DATABASE);
    when(mongoCollection.aggregate(anyList())).thenReturn(aggregateIterable);
    when(mongoCollection.find()).thenReturn(findIterable);
    when(changeStreamIterable.resumeAfter(resumeToken)).thenReturn(changeStreamIterable);

    // FindIterable setup
    when(findIterable.filter(any())).thenReturn(findIterable);
    when(findIterable.projection(any())).thenReturn(findIterable);
    when(findIterable.limit(anyInt())).thenReturn(findIterable);
    when(findIterable.sort(any())).thenReturn(findIterable);
    when(findIterable.cursor()).thenReturn(findCursor);
    when(findIterable.allowDiskUse(anyBoolean())).thenReturn(findIterable);
  }

  private void setupMultipleDatabases() {
    // Mock for first database
    final MongoDatabase mongoDatabase1 = mock(MongoDatabase.class);
    final MongoCollection mongoCollection1 = mock(MongoCollection.class);
    final FindIterable<Document> findIterable1 = mock(FindIterable.class);

    // Mock for second database
    final MongoDatabase mongoDatabase2 = mock(MongoDatabase.class);
    final MongoCollection mongoCollection2 = mock(MongoCollection.class);
    final FindIterable<Document> findIterable2 = mock(FindIterable.class);

    final BsonDocument resumeToken = ResumeTokens.fromData(RESUME_TOKEN);

    when(mongoClient.watch(BsonDocument.class)).thenReturn(changeStreamIterable);
    when(mongoClient.watch(MULTIPLE_DB_PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);

    // Setup first database (DATABASE)
    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase1);
    when(mongoDatabase1.watch(MULTIPLE_DB_PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);
    when(mongoDatabase1.getCollection(COLLECTION)).thenReturn(mongoCollection1);
    when(mongoDatabase1.getName()).thenReturn(DATABASE);
    when(mongoCollection1.aggregate(anyList())).thenReturn(aggregateIterable);
    when(mongoCollection1.find()).thenReturn(findIterable1);

    // Setup second database (DATABASE_1)
    when(mongoClient.getDatabase(DATABASE_1)).thenReturn(mongoDatabase2);
    when(mongoDatabase2.watch(MULTIPLE_DB_PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);
    when(mongoDatabase2.getCollection(COLLECTION_1)).thenReturn(mongoCollection2);
    when(mongoDatabase2.getName()).thenReturn(DATABASE_1);
    when(mongoCollection2.aggregate(anyList())).thenReturn(aggregateIterable);
    when(mongoCollection2.find()).thenReturn(findIterable2);

    // Resume token setup
    when(changeStreamIterable.resumeAfter(resumeToken)).thenReturn(changeStreamIterable);

    // FindIterable setup for first database
    when(findIterable1.filter(any())).thenReturn(findIterable1);
    when(findIterable1.projection(any())).thenReturn(findIterable1);
    when(findIterable1.limit(anyInt())).thenReturn(findIterable1);
    when(findIterable1.sort(any())).thenReturn(findIterable1);
    when(findIterable1.cursor()).thenReturn(findCursor);
    when(findIterable1.allowDiskUse(anyBoolean())).thenReturn(findIterable1);

    // FindIterable setup for second database
    when(findIterable2.filter(any())).thenReturn(findIterable2);
    when(findIterable2.projection(any())).thenReturn(findIterable2);
    when(findIterable2.limit(anyInt())).thenReturn(findIterable2);
    when(findIterable2.sort(any())).thenReturn(findIterable2);
    when(findIterable2.cursor()).thenReturn(findCursor);
    when(findIterable2.allowDiskUse(anyBoolean())).thenReturn(findIterable2);
  }

  @Test
  void testCreateCdcIteratorsEmptyInitialStateSingleDB() {
    setupSingleDatabase();
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null, SINGLE_DB_CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, SINGLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT,
            SINGLE_DB_CONFIG);
    assertNotNull(iterators);
    assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
    assertTrue(iterators.get(0).hasNext(),
        "Initial snapshot iterator should at least have one message if there's no initial snapshot state and collections are not empty");
  }

  @Test
  void testCreateCdcIteratorsEmptyInitialStateMultipleDB() {
    setupMultipleDatabases();
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null, MULTIPLE_DB_CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, MULTIPLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT,
            MULTIPLE_DB_CONFIG);
    assertNotNull(iterators);
    assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
    assertTrue(iterators.get(0).hasNext(),
        "Initial snapshot iterator should at least have one message if there's no initial snapshot state and collections are not empty");
  }

  @Test
  void testCreateCdcIteratorsEmptyInitialStateEmptyCollectionsSingleDB() {
    setupSingleDatabase();
    when(findCursor.hasNext()).thenReturn(false);
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null, SINGLE_DB_CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, SINGLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT,
            SINGLE_DB_CONFIG);
    assertNotNull(iterators);
    assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
  }

  @Test
  void testCreateCdcIteratorsEmptyInitialStateEmptyCollectionsMultipleDB() {
    setupMultipleDatabases();
    when(findCursor.hasNext()).thenReturn(false);
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null, MULTIPLE_DB_CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, MULTIPLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT,
            MULTIPLE_DB_CONFIG);
    assertNotNull(iterators);
    assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
  }

  @Test
  void testCreateCdcIteratorsFromInitialStateWithInProgressInitialSnapshotSingleDB() {
    setupSingleDatabase();
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumStateSingleDB(InitialSnapshotStatus.IN_PROGRESS), SINGLE_DB_CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, SINGLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT,
            SINGLE_DB_CONFIG);
    assertNotNull(iterators);
    assertEquals(4, iterators.size(), "Should always have 4 iterators: 1 for the cdc stream, 1 for the initial snapshot and 2 for CDC status");
    assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the cdc stream, and 1 for the initial snapshot");
    assertTrue(iterators.get(2).hasNext(),
        "Initial snapshot iterator should at least have one message if the initial snapshot state is set as in progress");
    final AirbyteMessage collectionStreamMessage = iterators.get(2).next();
    assertEquals(AirbyteMessage.Type.RECORD, collectionStreamMessage.getType());
    assertEquals(COLLECTION, collectionStreamMessage.getRecord().getStream());
  }

  // @Test
  // void testCreateCdcIteratorsFromInitialStateWithInProgressInitialSnapshotMultipleDB() {
  // setupMultipleDatabases();
  // List<String> databaseNames = MULTIPLE_DB_CONFIG.getDatabaseNames();
  // System.out.println("DEBUG: Database names from config: " + databaseNames);
  // System.out.println("DEBUG: Database count: " + databaseNames.size());
  // final MongoDbStateManager stateManager =
  // MongoDbStateManager.createStateManager(createInitialDebeziumStateMultipleDB(InitialSnapshotStatus.IN_PROGRESS),
  // MULTIPLE_DB_CONFIG);
  // final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
  // .createCdcIterators(mongoClient, cdcConnectorMetadataInjector,
  // MULTIPLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT, MULTIPLE_DB_CONFIG);
  // assertNotNull(iterators);
  // assertEquals(6, iterators.size(), "Should always have 6 iterators: 1 for the cdc stream, 1 for
  // the initial snapshot, 2 for CDC status for each stream");
  // assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the
  // cdc stream, and 1 for the initial snapshot");
  // assertTrue(iterators.get(2).hasNext(),
  // "Initial snapshot iterator should at least have one message if the initial snapshot state is set
  // as in progress");
  // final AirbyteMessage collectionStreamMessage = iterators.get(2).next();
  // assertEquals(AirbyteMessage.Type.RECORD, collectionStreamMessage.getType());
  // assertEquals(COLLECTION, collectionStreamMessage.getRecord().getStream());
  // }

  @Test
  void testCreateCdcIteratorsFromInitialStateWithCompletedInitialSnapshotSingleDB() {
    setupSingleDatabase();
    when(findCursor.hasNext()).thenReturn(false);
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumStateSingleDB(InitialSnapshotStatus.COMPLETE), SINGLE_DB_CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, SINGLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT,
            SINGLE_DB_CONFIG);
    assertNotNull(iterators);
    assertEquals(1, filterTraceIterator(iterators).size(), "Should always have 1 iterator for the cdc stream (due to WASS)");
  }

  @Test
  void testCreateCdcIteratorsFromInitialStateWithCompletedInitialSnapshotMultipleDB() {
    setupMultipleDatabases();
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumStateMultipleDB(InitialSnapshotStatus.COMPLETE), MULTIPLE_DB_CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, MULTIPLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT,
            MULTIPLE_DB_CONFIG);
    assertNotNull(iterators);
    assertEquals(1, filterTraceIterator(iterators).size(), "Should always have 1 iterator for the cdc stream (due to WASS)");
  }

  @Test
  void testCreateCdcIteratorsWithCompletedInitialSnapshotSavedOffsetInvalidDefaultBehaviorSingleDB() {
    setupSingleDatabase();
    when(changeStreamIterable.cursor())
        .thenReturn(mongoChangeStreamCursor)
        .thenThrow(new MongoCommandException(new BsonDocument(), new ServerAddress()))
        .thenReturn(mongoChangeStreamCursor);
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumStateSingleDB(InitialSnapshotStatus.COMPLETE), SINGLE_DB_CONFIG);
    assertThrows(ConfigErrorException.class,
        () -> cdcInitializer.createCdcIterators(mongoClient, cdcConnectorMetadataInjector, SINGLE_DB_CONFIGURED_CATALOG_STREAMS,
            stateManager, EMITTED_AT, SINGLE_DB_CONFIG));
  }

  @Test
  void testCreateCdcIteratorsWithCompletedInitialSnapshotSavedOffsetInvalidDefaultBehaviorMultipleDB() {
    setupMultipleDatabases();
    when(changeStreamIterable.cursor())
        .thenReturn(mongoChangeStreamCursor)
        .thenThrow(new MongoCommandException(new BsonDocument(), new ServerAddress()))
        .thenReturn(mongoChangeStreamCursor);
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumStateMultipleDB(InitialSnapshotStatus.COMPLETE), MULTIPLE_DB_CONFIG);
    assertThrows(ConfigErrorException.class,
        () -> cdcInitializer.createCdcIterators(mongoClient, cdcConnectorMetadataInjector, MULTIPLE_DB_CONFIGURED_CATALOG_STREAMS,
            stateManager, EMITTED_AT, MULTIPLE_DB_CONFIG));
  }

  @Test
  void testCreateCdcIteratorsWithCompletedInitialSnapshotSavedOffsetFailOptionSingleDb() {
    setupSingleDatabase();
    when(changeStreamIterable.cursor())
        .thenReturn(mongoChangeStreamCursor)
        .thenThrow(new MongoCommandException(new BsonDocument(), new ServerAddress()))
        .thenReturn(mongoChangeStreamCursor);
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumStateSingleDB(InitialSnapshotStatus.COMPLETE), SINGLE_DB_CONFIG);
    assertThrows(ConfigErrorException.class,
        () -> cdcInitializer.createCdcIterators(mongoClient, cdcConnectorMetadataInjector, SINGLE_DB_CONFIGURED_CATALOG_STREAMS,
            stateManager, EMITTED_AT, SINGLE_DB_CONFIG));
  }

  @Test
  void testCreateCdcIteratorsWithCompletedInitialSnapshotSavedOffsetFailOptionMultipleDb() {
    setupMultipleDatabases();
    when(changeStreamIterable.cursor())
        .thenReturn(mongoChangeStreamCursor)
        .thenThrow(new MongoCommandException(new BsonDocument(), new ServerAddress()))
        .thenReturn(mongoChangeStreamCursor);
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumStateMultipleDB(InitialSnapshotStatus.COMPLETE), MULTIPLE_DB_CONFIG);
    assertThrows(ConfigErrorException.class,
        () -> cdcInitializer.createCdcIterators(mongoClient, cdcConnectorMetadataInjector, MULTIPLE_DB_CONFIGURED_CATALOG_STREAMS,
            stateManager, EMITTED_AT, MULTIPLE_DB_CONFIG));
  }

  @Test
  void testCreateCdcIteratorsWithCompletedInitialSnapshotSavedOffsetInvalidResyncOptionSingleDB() {
    setupSingleDatabase();
    MongoDbSourceConfig resyncConfig = new MongoDbSourceConfig(createSingleDbConfig(RESYNC_DATA_OPTION));
    when(changeStreamIterable.cursor())
        .thenReturn(mongoChangeStreamCursor)
        .thenThrow(new MongoCommandException(new BsonDocument(), new ServerAddress()))
        .thenReturn(mongoChangeStreamCursor);
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumStateSingleDB(InitialSnapshotStatus.COMPLETE), SINGLE_DB_CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, SINGLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT, resyncConfig);
    assertNotNull(iterators);
    assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
    assertTrue(iterators.get(0).hasNext(),
        "Initial snapshot iterator should at least have one message if its snapshot state is set as complete but needs to start over due to invalid saved offset");
  }

  // Need to check
  @Test
  void testCreateCdcIteratorsWithCompletedInitialSnapshotSavedOffsetInvalidResyncOptionMultipleDB() {
    setupMultipleDatabases();
    MongoDbSourceConfig resyncConfig = new MongoDbSourceConfig(createMultipleDbConfig(RESYNC_DATA_OPTION));
    when(changeStreamIterable.cursor())
        .thenReturn(mongoChangeStreamCursor)
        .thenThrow(new MongoCommandException(new BsonDocument(), new ServerAddress()))
        .thenReturn(mongoChangeStreamCursor);
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumStateMultipleDB(InitialSnapshotStatus.COMPLETE), MULTIPLE_DB_CONFIG);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators = cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, MULTIPLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT,
            resyncConfig);
    assertNotNull(iterators);
    assertEquals(2, filterTraceIterator(iterators).size(), "Should always have 2 iterators: 1 for the initial snapshot and 1 for the cdc stream");
    assertTrue(iterators.get(0).hasNext(),
        "Initial snapshot iterator should at least have one message if its snapshot state is set as complete but needs to start over due to invalid saved offset");
  }

  JsonNode createSingleDbConfig(String cdcCursorFailBehaviour) {
    setupSingleDatabase();
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(DATABASE_CONFIG_CONFIGURATION_KEY,
            Map.of(
                MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://host:12345/",
                MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY, List.of(DATABASE)))
        .put(INVALID_CDC_CURSOR_POSITION_PROPERTY, cdcCursorFailBehaviour)
        .build());
  }

  JsonNode createMultipleDbConfig(String cdcCursorFailBehaviour) {
    setupMultipleDatabases();
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(DATABASE_CONFIG_CONFIGURATION_KEY,
            Map.of(
                MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://host:12345/",
                MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY, List.of(DATABASE, DATABASE_1)))
        .put(INVALID_CDC_CURSOR_POSITION_PROPERTY, cdcCursorFailBehaviour)
        .build());
  }

  @Test
  void testUnableToExtractOffsetFromStateExceptionSingleDB() {
    setupSingleDatabase();
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumStateSingleDB(InitialSnapshotStatus.COMPLETE), SINGLE_DB_CONFIG);
    doReturn(Optional.empty()).when(mongoDbDebeziumStateUtil).savedOffset(any(), any(), any(), any());
    assertThrows(RuntimeException.class,
        () -> cdcInitializer.createCdcIterators(mongoClient, cdcConnectorMetadataInjector, SINGLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager,
            EMITTED_AT,
            SINGLE_DB_CONFIG));
  }

  @Test
  void testUnableToExtractOffsetFromStateExceptionMultipleDB() {
    setupMultipleDatabases();
    final MongoDbStateManager stateManager =
        MongoDbStateManager.createStateManager(createInitialDebeziumStateMultipleDB(InitialSnapshotStatus.COMPLETE), MULTIPLE_DB_CONFIG);
    doReturn(Optional.empty()).when(mongoDbDebeziumStateUtil).savedOffset(any(), any(), any(), any());
    assertThrows(RuntimeException.class,
        () -> cdcInitializer.createCdcIterators(mongoClient, cdcConnectorMetadataInjector, MULTIPLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager,
            EMITTED_AT,
            MULTIPLE_DB_CONFIG));
  }

  @Test
  void testUnsupportedIdTypeThrowsExceptionSingleDB() {
    setupSingleDatabase();
    final Document aggregate = Document.parse("{\"_id\": {\"_id\": \"exotic\"}, \"count\": 1}");

    when(aggregateCursor.hasNext()).thenReturn(true, false);
    when(aggregateCursor.next()).thenReturn(aggregate);
    doCallRealMethod().when(aggregateIterable).forEach(any(Consumer.class));

    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null, SINGLE_DB_CONFIG);

    final var thrown = assertThrows(ConfigErrorException.class, () -> cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, SINGLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT,
            SINGLE_DB_CONFIG));
    assertTrue(thrown.getMessage().contains("_id fields with the following types are currently supported"));
  }

  @Test
  void testUnsupportedIdTypeThrowsExceptionMultipleDB() {
    setupMultipleDatabases();
    final Document aggregate = Document.parse("{\"_id\": {\"_id\": \"exotic\"}, \"count\": 1}");

    when(aggregateCursor.hasNext()).thenReturn(true, false);
    when(aggregateCursor.next()).thenReturn(aggregate);
    doCallRealMethod().when(aggregateIterable).forEach(any(Consumer.class));

    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null, MULTIPLE_DB_CONFIG);

    final var thrown = assertThrows(ConfigErrorException.class, () -> cdcInitializer
        .createCdcIterators(mongoClient, cdcConnectorMetadataInjector, MULTIPLE_DB_CONFIGURED_CATALOG_STREAMS, stateManager, EMITTED_AT,
            MULTIPLE_DB_CONFIG));
    assertTrue(thrown.getMessage().contains("_id fields with the following types are currently supported"));
  }

  private static JsonNode createInitialDebeziumStateSingleDB(final InitialSnapshotStatus initialSnapshotStatus) {
    final StreamDescriptor streamDescriptor = new StreamDescriptor().withNamespace(STREAM_NAMESPACE).withName(STREAM_NAME);
    final MongoDbCdcState cdcState = new MongoDbCdcState(MongoDbDebeziumStateUtil.formatState("mongodb://host:12345/", RESUME_TOKEN1));
    final MongoDbStreamState mongoDbStreamState = new MongoDbStreamState(ID, initialSnapshotStatus, IdType.OBJECT_ID);
    final JsonNode sharedState = Jsons.jsonNode(cdcState);
    final JsonNode streamState = Jsons.jsonNode(mongoDbStreamState);
    final AirbyteStreamState airbyteStreamState = new AirbyteStreamState().withStreamDescriptor(streamDescriptor).withStreamState(streamState);
    final AirbyteGlobalState airbyteGlobalState = new AirbyteGlobalState().withSharedState(sharedState).withStreamStates(List.of(airbyteStreamState));
    final AirbyteStateMessage airbyteStateMessage =
        new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.GLOBAL).withGlobal(airbyteGlobalState);
    return Jsons.jsonNode(List.of(airbyteStateMessage));
  }

  private static JsonNode createInitialDebeziumStateMultipleDB(final InitialSnapshotStatus initialSnapshotStatus) {
    final StreamDescriptor streamDescriptor = new StreamDescriptor().withNamespace(STREAM_NAMESPACE).withName(STREAM_NAME);
    final StreamDescriptor streamDescriptor_1 = new StreamDescriptor().withNamespace(STREAM_NAMESPACE_1).withName(STREAM_NAME_1);
    final MongoDbCdcState cdcState = new MongoDbCdcState(MongoDbDebeziumStateUtil.formatState("mongodb://host:12345/", RESUME_TOKEN1));
    final MongoDbStreamState mongoDbStreamState = new MongoDbStreamState(ID, initialSnapshotStatus, IdType.OBJECT_ID);
    final JsonNode sharedState = Jsons.jsonNode(cdcState);
    final JsonNode streamState = Jsons.jsonNode(mongoDbStreamState);

    // Create stream states for both databases (DATABASE + COLLECTION AND DATABASE_1 + COLLECTION_1)
    final AirbyteStreamState airbyteStreamState1 = new AirbyteStreamState().withStreamDescriptor(streamDescriptor).withStreamState(streamState);
    final AirbyteStreamState airbyteStreamState2 = new AirbyteStreamState().withStreamDescriptor(streamDescriptor_1).withStreamState(streamState);

    final AirbyteGlobalState airbyteGlobalState = new AirbyteGlobalState()
        .withSharedState(sharedState)
        .withStreamStates(List.of(airbyteStreamState1, airbyteStreamState2)); // Both stream states

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
