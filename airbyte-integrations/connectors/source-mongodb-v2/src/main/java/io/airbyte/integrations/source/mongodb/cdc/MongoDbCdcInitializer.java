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
import io.airbyte.cdk.integrations.source.relationaldb.streamstatus.StreamStatusTraceEmitterIterator;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mongodb.InitialSnapshotHandler;
import io.airbyte.integrations.source.mongodb.MongoDbSourceConfig;
import io.airbyte.integrations.source.mongodb.MongoUtil;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.protocol.models.v0.*;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.function.Supplier;
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
    final int queueSize = MongoUtil.getDebeziumEventQueueSize(config);
    final String databaseName = config.getDatabaseName();
    final boolean isEnforceSchema = config.getEnforceSchema();
    final Properties defaultDebeziumProperties = MongoDbCdcProperties.getDebeziumProperties();
    logOplogInfo(mongoClient);
    final BsonDocument initialResumeToken =
        MongoDbResumeTokenHelper.getMostRecentResumeToken(mongoClient, databaseName, incrementalOnlyStreamsCatalog);
    final JsonNode initialDebeziumState =
        mongoDbDebeziumStateUtil.constructInitialDebeziumState(initialResumeToken, mongoClient, databaseName);
    final MongoDbCdcState cdcState =
        (stateManager.getCdcState() == null || stateManager.getCdcState().state() == null || stateManager.getCdcState().state().isNull())
            ? new MongoDbCdcState(initialDebeziumState, isEnforceSchema)
            : new MongoDbCdcState(Jsons.clone(stateManager.getCdcState().state()), stateManager.getCdcState().schema_enforced());
    final Optional<BsonDocument> optSavedOffset = mongoDbDebeziumStateUtil.savedOffset(
        Jsons.clone(defaultDebeziumProperties),
        incrementalOnlyStreamsCatalog,
        cdcState.state(),
        config.getDatabaseConfig(),
        mongoClient);

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
    final List<AutoCloseableIterator<AirbyteMessage>> initialSnapshotIterators =
        initialSnapshotHandler.getIterators(initialSnapshotStreams, stateManager, mongoClient.getDatabase(databaseName),
            config, true, false);

    final AirbyteDebeziumHandler<BsonTimestamp> handler = new AirbyteDebeziumHandler<>(config.getDatabaseConfig(),
        new MongoDbCdcTargetPosition(initialResumeToken), false, firstRecordWaitTime, queueSize, false);
    final MongoDbCdcStateHandler mongoDbCdcStateHandler = new MongoDbCdcStateHandler(stateManager);
    final MongoDbCdcSavedInfoFetcher cdcSavedInfoFetcher = new MongoDbCdcSavedInfoFetcher(stateToBeUsed);
    final var propertiesManager =
        new MongoDbDebeziumPropertiesManager(defaultDebeziumProperties, config.getDatabaseConfig(), incrementalOnlyStreamsCatalog);
    final var eventConverter =
        new MongoDbDebeziumEventConverter(cdcMetadataInjector, incrementalOnlyStreamsCatalog, emittedAt, config.getDatabaseConfig());

    final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(
        propertiesManager, eventConverter, cdcSavedInfoFetcher, mongoDbCdcStateHandler);

    // We can close the client after the initial snapshot is complete, incremental
    // iterator does not make use of the client.
    final AutoCloseableIterator<AirbyteMessage> initialSnapshotIterator = AutoCloseableIterators.appendOnClose(
        AutoCloseableIterators.concatWithEagerClose(initialSnapshotIterators), mongoClient::close);

    final List<AutoCloseableIterator<AirbyteMessage>> cdcStreamsStartStatusEmitters = incrementalOnlyStreamsCatalog.getStreams().stream()
        .filter(stream -> !initialSnapshotStreams.contains(stream))
        .map(stream -> (AutoCloseableIterator<AirbyteMessage>) new StreamStatusTraceEmitterIterator(new AirbyteStreamStatusHolder(
            new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace()),
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED)))
        .toList();

    final List<AutoCloseableIterator<AirbyteMessage>> cdcStreamsCompleteStatusEmitters = incrementalOnlyStreamsCatalog.getStreams().stream()
        .map(stream -> (AutoCloseableIterator<AirbyteMessage>) new StreamStatusTraceEmitterIterator(new AirbyteStreamStatusHolder(
            new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace()),
            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE)))
        .toList();

    return Stream.of(Collections.singletonList(initialSnapshotIterator), cdcStreamsStartStatusEmitters,
        Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier, null)),
        cdcStreamsCompleteStatusEmitters).flatMap(Collection::stream).toList();
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
