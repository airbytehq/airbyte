/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.COLLECTION_STATISTICS_COUNT_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.COLLECTION_STATISTICS_STORAGE_SIZE_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoDatabase;
import io.airbyte.integrations.source.mongodb.internal.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStreamState;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;
import java.util.Map;
import org.bson.Document;
import org.junit.jupiter.api.Test;

class MongoDbCdcInitialSnapshotUtilsTest {

  private static final String NAMESPACE = "namespace";
  private static final String COMPLETED_NAME = "completed";
  private static final String IN_PROGRESS_NAME = "in_progress";
  private static final String NEW_NAME = "new";

  @Test
  void testRetrieveInitialSnapshotIterators() {
    final MongoDbStateManager stateManager = mock(MongoDbStateManager.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final ConfiguredAirbyteStream completedStream = createConfiguredAirbyteStream(COMPLETED_NAME, NAMESPACE);
    final ConfiguredAirbyteStream inProgressStream = createConfiguredAirbyteStream(IN_PROGRESS_NAME, NAMESPACE);
    final ConfiguredAirbyteStream newStream = createConfiguredAirbyteStream(NEW_NAME, NAMESPACE);
    final List<ConfiguredAirbyteStream> configuredStreams = List.of(completedStream, inProgressStream, newStream);
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(configuredStreams);
    final boolean savedOffsetAfterResumeToken = true;

    when(stateManager.getStreamStates()).thenReturn(Map.of(
        new AirbyteStreamNameNamespacePair(COMPLETED_NAME, NAMESPACE), new MongoDbStreamState("1", InitialSnapshotStatus.COMPLETE),
        new AirbyteStreamNameNamespacePair(IN_PROGRESS_NAME, NAMESPACE), new MongoDbStreamState("2", InitialSnapshotStatus.IN_PROGRESS)));
    when(mongoDatabase.runCommand(any()))
        .thenReturn(new Document(Map.of(COLLECTION_STATISTICS_STORAGE_SIZE_KEY, 1000000L, COLLECTION_STATISTICS_COUNT_KEY, 10000)));
    when(mongoClient.getDatabase(NAMESPACE)).thenReturn(mongoDatabase);

    final List<ConfiguredAirbyteStream> initialSnapshotStreams =
        MongoDbCdcInitialSnapshotUtils.getStreamsForInitialSnapshot(mongoClient, stateManager, catalog, savedOffsetAfterResumeToken);
    assertEquals(2, initialSnapshotStreams.size());
    assertTrue(initialSnapshotStreams.contains(inProgressStream));
    assertTrue(initialSnapshotStreams.contains(newStream));
  }

  @Test
  void testRetrieveInitialSnapshotIteratorsSavedOffsetNotAfterResumeToken() {
    final MongoDbStateManager stateManager = mock(MongoDbStateManager.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final ConfiguredAirbyteStream completedStream = createConfiguredAirbyteStream(COMPLETED_NAME, NAMESPACE);
    final ConfiguredAirbyteStream inProgressStream = createConfiguredAirbyteStream(IN_PROGRESS_NAME, NAMESPACE);
    final ConfiguredAirbyteStream newStream = createConfiguredAirbyteStream(NEW_NAME, NAMESPACE);
    final List<ConfiguredAirbyteStream> configuredStreams = List.of(completedStream, inProgressStream, newStream);
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(configuredStreams);
    final boolean savedOffsetAfterResumeToken = false;

    when(mongoDatabase.runCommand(any()))
        .thenReturn(new Document(Map.of(COLLECTION_STATISTICS_STORAGE_SIZE_KEY, 1000000L, COLLECTION_STATISTICS_COUNT_KEY, 10000)));
    when(mongoClient.getDatabase(NAMESPACE)).thenReturn(mongoDatabase);

    final List<ConfiguredAirbyteStream> initialSnapshotStreams =
        MongoDbCdcInitialSnapshotUtils.getStreamsForInitialSnapshot(mongoClient, stateManager, catalog, savedOffsetAfterResumeToken);

    assertEquals(3, initialSnapshotStreams.size());
    assertTrue(initialSnapshotStreams.contains(completedStream));
    assertTrue(initialSnapshotStreams.contains(inProgressStream));
    assertTrue(initialSnapshotStreams.contains(newStream));
  }

  @Test
  void testFailureToGenerateEstimateDoesNotImpactSync() {
    final MongoDbStateManager stateManager = mock(MongoDbStateManager.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final ConfiguredAirbyteStream completedStream = createConfiguredAirbyteStream(COMPLETED_NAME, NAMESPACE);
    final ConfiguredAirbyteStream inProgressStream = createConfiguredAirbyteStream(IN_PROGRESS_NAME, NAMESPACE);
    final ConfiguredAirbyteStream newStream = createConfiguredAirbyteStream(NEW_NAME, NAMESPACE);
    final List<ConfiguredAirbyteStream> configuredStreams = List.of(completedStream, inProgressStream, newStream);
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(configuredStreams);
    final boolean savedOffsetAfterResumeToken = true;

    when(stateManager.getStreamStates()).thenReturn(Map.of(
        new AirbyteStreamNameNamespacePair(COMPLETED_NAME, NAMESPACE), new MongoDbStreamState("1", InitialSnapshotStatus.COMPLETE),
        new AirbyteStreamNameNamespacePair(IN_PROGRESS_NAME, NAMESPACE), new MongoDbStreamState("2", InitialSnapshotStatus.IN_PROGRESS)));
    when(mongoClient.getDatabase(NAMESPACE)).thenThrow(new IllegalArgumentException("test"));

    final List<ConfiguredAirbyteStream> initialSnapshotStreams =
        MongoDbCdcInitialSnapshotUtils.getStreamsForInitialSnapshot(mongoClient, stateManager, catalog, savedOffsetAfterResumeToken);
    assertEquals(2, initialSnapshotStreams.size());
    assertTrue(initialSnapshotStreams.contains(inProgressStream));
    assertTrue(initialSnapshotStreams.contains(newStream));
  }

  @Test
  void testMissingCollectionStatisticsDoNotImpactSync() {
    final MongoDbStateManager stateManager = mock(MongoDbStateManager.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final ConfiguredAirbyteStream completedStream = createConfiguredAirbyteStream(COMPLETED_NAME, NAMESPACE);
    final ConfiguredAirbyteStream inProgressStream = createConfiguredAirbyteStream(IN_PROGRESS_NAME, NAMESPACE);
    final ConfiguredAirbyteStream newStream = createConfiguredAirbyteStream(NEW_NAME, NAMESPACE);
    final List<ConfiguredAirbyteStream> configuredStreams = List.of(completedStream, inProgressStream, newStream);
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(configuredStreams);
    final boolean savedOffsetAfterResumeToken = true;

    when(stateManager.getStreamStates()).thenReturn(Map.of(
        new AirbyteStreamNameNamespacePair(COMPLETED_NAME, NAMESPACE), new MongoDbStreamState("1", InitialSnapshotStatus.COMPLETE),
        new AirbyteStreamNameNamespacePair(IN_PROGRESS_NAME, NAMESPACE), new MongoDbStreamState("2", InitialSnapshotStatus.IN_PROGRESS)));
    when(mongoClient.getDatabase(NAMESPACE)).thenReturn(mongoDatabase);

    final List<ConfiguredAirbyteStream> initialSnapshotStreams =
        MongoDbCdcInitialSnapshotUtils.getStreamsForInitialSnapshot(mongoClient, stateManager, catalog, savedOffsetAfterResumeToken);
    assertEquals(2, initialSnapshotStreams.size());
    assertTrue(initialSnapshotStreams.contains(inProgressStream));
    assertTrue(initialSnapshotStreams.contains(newStream));
  }

  private AirbyteStream createAirbyteStream(final String name, final String namespace) {
    return new AirbyteStream().withName(name).withNamespace(namespace);
  }

  private ConfiguredAirbyteStream createConfiguredAirbyteStream(final String name, final String namespace) {
    return new ConfiguredAirbyteStream()
        .withStream(createAirbyteStream(name, namespace))
        .withSyncMode(SyncMode.INCREMENTAL);
  }

}
