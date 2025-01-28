/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.cdk.db.DbAnalyticsUtils.cdcCursorInvalidMessage;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoDatabase;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.cdk.integrations.source.relationaldb.InitialLoadTimeoutUtil;
import io.airbyte.cdk.integrations.source.relationaldb.streamstatus.StreamStatusTraceEmitterIterator;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mongodb.InitialSnapshotHandler;
import io.airbyte.integrations.source.mongodb.MongoDbSourceConfig;
import io.airbyte.integrations.source.mongodb.MongoUtil;
import io.airbyte.integrations.source.mongodb.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.protocol.models.v0.*;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.bson.Document;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Provides methods to initialize the stream iterators based on the state of each stream in the
 * configured catalog.
 * <p />
 * <p />
 * For more information on the iterator selection logic, see
 * {@link MongoDbCdcInitialSnapshotUtils#getStreamsForInitialSnapshot(MongoClient, MongoDbStateManager, ConfiguredAirbyteCatalog, boolean)}
 * and {@link AirbyteDebeziumHandler#getIncrementalIterators}
 */
public class MongoDbCdcInitializer {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbCdcInitializer.class);

  private final MongoDbDebeziumStateUtil mongoDbDebeziumStateUtil;

  @VisibleForTesting
  MongoDbCdcInitializer(final MongoDbDebeziumStateUtil mongoDbDebeziumStateUtil) {
    this.mongoDbDebeziumStateUtil = mongoDbDebeziumStateUtil;
  }

  public MongoDbCdcInitializer() {
    this(new MongoDbDebeziumStateUtil());
  }

  /**
   * Generates the list of stream iterators based on the configured catalog and stream state. This
   * list will include any initial snapshot iterators, followed by incremental iterators, where
   * applicable.
   *
   * @param mongoClient The {@link MongoClient} used to interact with the target MongoDB server.
   * @param cdcMetadataInjector The {@link MongoDbCdcConnectorMetadataInjector} used to add metadata
   *        to generated records.
   * @param streams The configured Airbyte catalog of streams for the source.
   * @param stateManager The {@link MongoDbStateManager} that provides state information used for
   *        iterator selection.
   * @param emittedAt The timestamp of the sync.
   * @param config The configuration of the source.
   * @return The list of stream iterators with initial snapshot iterators before any incremental
   *         iterators.
   */
  public List<AutoCloseableIterator<AirbyteMessage>> createCdcIterators(
                                                                        final MongoClient mongoClient,
                                                                        final MongoDbCdcConnectorMetadataInjector cdcMetadataInjector,
                                                                        final List<ConfiguredAirbyteStream> streams,
                                                                        final MongoDbStateManager stateManager,
                                                                        final Instant emittedAt,
                                                                        final MongoDbSourceConfig config) {

    ConfiguredAirbyteCatalog incrementalOnlyStreamsCatalog = new ConfiguredAirbyteCatalog().withStreams(streams);
    final Duration firstRecordWaitTime = Duration.ofSeconds(config.getInitialWaitingTimeSeconds());
    // #35059: debezium heartbeats are not sent on the expected interval. this is
    // a workaround to allow making subsequent wait time configurable.
    final Duration subsequentRecordWaitTime = firstRecordWaitTime;
    LOGGER.info("Subsequent cdc record wait time: {} seconds", subsequentRecordWaitTime);
    final Duration initialLoadTimeout = InitialLoadTimeoutUtil.getInitialLoadTimeout(config.rawConfig());

    final int queueSize = MongoUtil.getDebeziumEventQueueSize(config);
    final String databaseName = config.getDatabaseName();
    final boolean isEnforceSchema = config.getEnforceSchema();

    final Properties defaultDebeziumProperties = MongoDbCdcProperties.getDebeziumProperties();
    logOplogInfo(mongoClient);

    final BsonDocument initialResumeToken =
        MongoDbResumeTokenHelper.getMostRecentResumeToken(mongoClient, databaseName, incrementalOnlyStreamsCatalog);
    final JsonNode initialDebeziumState =
        mongoDbDebeziumStateUtil.constructInitialDebeziumState(initialResumeToken, databaseName);

    final MongoDbCdcState cdcState =
        (stateManager.getCdcState() == null || stateManager.getCdcState().state() == null || stateManager.getCdcState().state().isNull())
            ? new MongoDbCdcState(initialDebeziumState, isEnforceSchema)
            : new MongoDbCdcState(Jsons.clone(stateManager.getCdcState().state()), stateManager.getCdcState().schema_enforced());

    final Optional<BsonDocument> optSavedOffset = mongoDbDebeziumStateUtil.savedOffset(
        Jsons.clone(defaultDebeziumProperties),
        incrementalOnlyStreamsCatalog,
        cdcState.state(),
        config.getDatabaseConfig());

    // We should always be able to extract offset out of state if it's not null
    if (cdcState.state() != null && optSavedOffset.isEmpty()) {
      throw new RuntimeException(
          "Unable extract the offset out of state, State mutation might not be working. " + cdcState.state());
    }

    final boolean savedOffsetIsValid =
        optSavedOffset
            .filter(savedOffset -> mongoDbDebeziumStateUtil.isValidResumeToken(savedOffset, mongoClient, databaseName, incrementalOnlyStreamsCatalog))
            .isPresent();

    if (!savedOffsetIsValid) {
      AirbyteTraceMessageUtility.emitAnalyticsTrace(cdcCursorInvalidMessage());
      if (config.shouldFailSyncOnInvalidCursor()) {
        throw new ConfigErrorException(
            "Saved offset is not valid. Please reset the connection, and then increase oplog retention and/or increase sync frequency to prevent his from happening in the future. See https://docs.airbyte.com/integrations/sources/mongodb-v2#mongodb-oplog-and-change-streams for more details");
      }

      LOGGER.info("Saved offset is not valid. Airbyte will trigger a full refresh.");
      // If the offset in the state is invalid, reset the state to the initial STATE
      stateManager.resetState(new MongoDbCdcState(initialDebeziumState, config.getEnforceSchema()));
    } else {
      LOGGER.info("Valid offset state discovered. Updating state manager with retrieved CDC state {} {}...", cdcState.state(),
          cdcState.schema_enforced());
      stateManager.updateCdcState(new MongoDbCdcState(cdcState.state(), cdcState.schema_enforced()));
    }

    final MongoDbCdcState stateToBeUsed =
        (!savedOffsetIsValid || stateManager.getCdcState() == null || stateManager.getCdcState().state() == null
            || stateManager.getCdcState().state().isNull())
                ? new MongoDbCdcState(initialDebeziumState, config.getEnforceSchema())
                : stateManager.getCdcState();

    final List<ConfiguredAirbyteStream> initialSnapshotStreams =
        MongoDbCdcInitialSnapshotUtils.getStreamsForInitialSnapshot(mongoClient, stateManager, incrementalOnlyStreamsCatalog, savedOffsetIsValid);
    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();

    final Set<AirbyteStreamNameNamespacePair> streamsStillInInitialSnapshot = stateManager.getStreamStates().entrySet().stream()
        .filter(e -> InitialSnapshotStatus.IN_PROGRESS.equals(e.getValue().status()))
        .map(Map.Entry::getKey)
        .collect(Collectors.toSet());

    // Fetch the streams from the catalog that still need to complete the initial snapshot sync
    List<ConfiguredAirbyteStream> inProgressSnapshotStreams = new ArrayList<>(incrementalOnlyStreamsCatalog.getStreams().stream()
        .filter(stream -> streamsStillInInitialSnapshot.contains(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.getStream())))
        .map(Jsons::clone)
        .toList());
    final var startedCdcStreamList = incrementalOnlyStreamsCatalog.getStreams().stream()
        .filter(stream -> (!initialSnapshotStreams.contains(stream) || inProgressSnapshotStreams.contains(stream)))
        .map(stream -> stream.getStream().getNamespace() + "\\." + stream.getStream().getName()).toList();

    final List<AutoCloseableIterator<AirbyteMessage>> initialSnapshotIterators =
        initialSnapshotHandler.getIterators(initialSnapshotStreams, stateManager, mongoClient.getDatabase(databaseName),
            config, false, false, emittedAt, Optional.of(initialLoadTimeout));

    final AirbyteDebeziumHandler<BsonTimestamp> handler = new AirbyteDebeziumHandler<>(config.getDatabaseConfig(),
        new MongoDbCdcTargetPosition(initialResumeToken), false, firstRecordWaitTime, queueSize, false);

    final MongoDbCdcStateHandler mongoDbCdcStateHandler = new MongoDbCdcStateHandler(stateManager);
    final MongoDbCdcSavedInfoFetcher cdcSavedInfoFetcher = new MongoDbCdcSavedInfoFetcher(stateToBeUsed);

    final var cdcStreamList = incrementalOnlyStreamsCatalog.getStreams().stream()
        .filter(stream -> stream.getSyncMode() == SyncMode.INCREMENTAL)
        .map(s -> s.getStream().getNamespace() + "\\." + s.getStream().getName())
        .toList();

    // We can close the client after the initial snapshot is complete, incremental
    // iterator does not make use of the client.
    final AutoCloseableIterator<AirbyteMessage> initialSnapshotIterator = AutoCloseableIterators.appendOnClose(
        AutoCloseableIterators.concatWithEagerClose(initialSnapshotIterators), mongoClient::close);

    final List<AutoCloseableIterator<AirbyteMessage>> cdcStreamsStartStatusEmitters = incrementalOnlyStreamsCatalog.getStreams().stream()
        .map(stream -> (AutoCloseableIterator<AirbyteMessage>) new StreamStatusTraceEmitterIterator(new AirbyteStreamStatusHolder(
            new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace()),
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED)))
        .toList();

    final List<AutoCloseableIterator<AirbyteMessage>> cdcStreamsCompleteStatusEmitters = incrementalOnlyStreamsCatalog.getStreams().stream()
        .map(stream -> (AutoCloseableIterator<AirbyteMessage>) new StreamStatusTraceEmitterIterator(new AirbyteStreamStatusHolder(
            new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace()),
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE)))
        .toList();

    if (startedCdcStreamList.isEmpty()) {
      LOGGER.info("First sync - no cdc streams have been completed or started");
      /*
       * This is the first run case - no initial loads have been started. In this case, we want to run the
       * iterators in the following order: 1. Run the initial load iterators. This step will timeout and
       * throw a transient error if run for too long (> 8hrs by default). 2. Run the debezium iterators
       * with ALL of the incremental streams configured. This is because if step 1 completes, the initial
       * load can be considered finished.
       */
      final var propertiesManager =
          new MongoDbDebeziumPropertiesManager(defaultDebeziumProperties, config.getDatabaseConfig(), incrementalOnlyStreamsCatalog, cdcStreamList);
      final var eventConverter =
          new MongoDbDebeziumEventConverter(cdcMetadataInjector, incrementalOnlyStreamsCatalog, emittedAt, config.getDatabaseConfig());
      final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(
          propertiesManager, eventConverter, cdcSavedInfoFetcher, mongoDbCdcStateHandler);

      return Stream.of(
          cdcStreamsStartStatusEmitters,
          Collections.singletonList(initialSnapshotIterator),
          Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier, null)),
          cdcStreamsCompleteStatusEmitters).flatMap(Collection::stream).toList();
    } else if (initialSnapshotIterators.isEmpty()) {
      LOGGER.info("Initial load has finished completely - only reading the oplog");
      /*
       * In this case, the initial load has completed and only debezium should be run. The iterators
       * should be run in the following order: 1. Run the debezium iterators with ALL of the incremental
       * streams configured.
       */
      final var propertiesManager =
          new MongoDbDebeziumPropertiesManager(defaultDebeziumProperties, config.getDatabaseConfig(), incrementalOnlyStreamsCatalog, cdcStreamList);
      final var eventConverter =
          new MongoDbDebeziumEventConverter(cdcMetadataInjector, incrementalOnlyStreamsCatalog, emittedAt, config.getDatabaseConfig());
      final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(
          propertiesManager, eventConverter, cdcSavedInfoFetcher, mongoDbCdcStateHandler);
      return Stream.of(
          cdcStreamsStartStatusEmitters,
          Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier, null)),
          cdcStreamsCompleteStatusEmitters).flatMap(Collection::stream).toList();
    } else {
      LOGGER.info("Initial load is in progress - reading oplog first and then resuming with initial load.");
      /*
       * In this case, the initial load has partially completed (WASS case). The iterators should be run
       * in the following order: 1. Run the debezium iterators with only the incremental streams which
       * have been fully or partially completed configured. 2. Resume initial load for partially completed
       * and not started streams. This step will timeout and throw a transient error if run for too long
       * (> 8hrs by default). 3. Emit a transient error. This is to signal to the platform to restart the
       * sync to clear the oplog. We cannot simply add the same cdc iterators as their target end position
       * is fixed to the tip of the oplog at the start of the sync.
       */
      final var propertiesManager =
          new MongoDbDebeziumPropertiesManager(defaultDebeziumProperties, config.getDatabaseConfig(), incrementalOnlyStreamsCatalog,
              startedCdcStreamList);
      final var eventConverter =
          new MongoDbDebeziumEventConverter(cdcMetadataInjector, incrementalOnlyStreamsCatalog, emittedAt, config.getDatabaseConfig());
      final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(
          propertiesManager, eventConverter, cdcSavedInfoFetcher, mongoDbCdcStateHandler);
      return Stream.of(
          cdcStreamsStartStatusEmitters,
          Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier, null)),
          Collections.singletonList(initialSnapshotIterator),
          cdcStreamsCompleteStatusEmitters)
          .flatMap(Collection::stream).toList();
    }
  }

  private void logOplogInfo(final MongoClient mongoClient) {
    try {
      final MongoDatabase localDatabase = mongoClient.getDatabase("local");
      final Document command = new Document("collStats", "oplog.rs");
      final Document result = localDatabase.runCommand(command);
      if (result != null) {
        LOGGER.info("Max oplog size is {} bytes", result.getLong("maxSize"));
        LOGGER.info("Free space in oplog is {} bytes", result.getLong("freeStorageSize"));
      }
    } catch (final Exception e) {
      LOGGER.warn("Unable to query for op log stats, exception: {}" + e.getMessage());
    }
  }

}
