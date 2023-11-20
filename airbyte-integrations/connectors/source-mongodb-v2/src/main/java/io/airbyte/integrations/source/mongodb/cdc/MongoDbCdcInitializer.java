/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.MongoClient;
import io.airbyte.cdk.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.cdk.integrations.debezium.internals.FirstRecordWaitTimeUtil;
import io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbCdcTargetPosition;
import io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumStateUtil;
import io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbResumeTokenHelper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mongodb.InitialSnapshotHandler;
import io.airbyte.integrations.source.mongodb.MongoDbSourceConfig;
import io.airbyte.integrations.source.mongodb.MongoUtil;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.Properties;
import java.util.function.Supplier;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
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
   * @param catalog The configured Airbyte catalog of streams for the source.
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
                                                                        final ConfiguredAirbyteCatalog catalog,
                                                                        final MongoDbStateManager stateManager,
                                                                        final Instant emittedAt,
                                                                        final MongoDbSourceConfig config) {

    final Duration firstRecordWaitTime = FirstRecordWaitTimeUtil.getFirstRecordWaitTime(config.rawConfig());
    final OptionalInt queueSize = MongoUtil.getDebeziumEventQueueSize(config);
    final String databaseName = config.getDatabaseName();
    final Properties defaultDebeziumProperties = MongoDbCdcProperties.getDebeziumProperties();
    final BsonDocument resumeToken = MongoDbResumeTokenHelper.getMostRecentResumeToken(mongoClient);
    final JsonNode initialDebeziumState =
        mongoDbDebeziumStateUtil.constructInitialDebeziumState(resumeToken, mongoClient, databaseName);
    final JsonNode cdcState = (stateManager.getCdcState() == null || stateManager.getCdcState().state() == null) ? initialDebeziumState
        : Jsons.clone(stateManager.getCdcState().state());
    final Optional<BsonDocument> optSavedOffset = mongoDbDebeziumStateUtil.savedOffset(
        Jsons.clone(defaultDebeziumProperties),
        catalog,
        cdcState,
        config.rawConfig(),
        mongoClient);

    // We should always be able to extract offset out of state if it's not null
    if (cdcState != null && optSavedOffset.isEmpty()) {
      throw new RuntimeException(
          "Unable extract the offset out of state, State mutation might not be working. " + cdcState);
    }

    final boolean savedOffsetIsValid =
        optSavedOffset.filter(savedOffset -> mongoDbDebeziumStateUtil.isValidResumeToken(savedOffset, mongoClient)).isPresent();

    if (!savedOffsetIsValid) {
      LOGGER.debug("Saved offset is not valid. Airbyte will trigger a full refresh.");
      // If the offset in the state is invalid, reset the state to the initial STATE
      stateManager.resetState(new MongoDbCdcState(initialDebeziumState));
    } else {
      LOGGER.debug("Valid offset state discovered.  Updating state manager with retrieved CDC state {}...", cdcState);
      stateManager.updateCdcState(new MongoDbCdcState(cdcState));
    }

    final MongoDbCdcState stateToBeUsed =
        (!savedOffsetIsValid || stateManager.getCdcState() == null || stateManager.getCdcState().state() == null)
            ? new MongoDbCdcState(initialDebeziumState)
            : stateManager.getCdcState();

    final List<ConfiguredAirbyteStream> initialSnapshotStreams =
        MongoDbCdcInitialSnapshotUtils.getStreamsForInitialSnapshot(mongoClient, stateManager, catalog, savedOffsetIsValid);
    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    final List<AutoCloseableIterator<AirbyteMessage>> initialSnapshotIterators =
        initialSnapshotHandler.getIterators(initialSnapshotStreams, stateManager, mongoClient.getDatabase(databaseName), cdcMetadataInjector,
            emittedAt, config.getCheckpointInterval());

    final AirbyteDebeziumHandler<BsonTimestamp> handler = new AirbyteDebeziumHandler<>(config.rawConfig(),
        new MongoDbCdcTargetPosition(resumeToken), false, firstRecordWaitTime, queueSize);
    final MongoDbCdcStateHandler mongoDbCdcStateHandler = new MongoDbCdcStateHandler(stateManager);
    final MongoDbCdcSavedInfoFetcher cdcSavedInfoFetcher = new MongoDbCdcSavedInfoFetcher(stateToBeUsed);

    final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(catalog,
        cdcSavedInfoFetcher,
        mongoDbCdcStateHandler,
        cdcMetadataInjector,
        defaultDebeziumProperties,
        DebeziumPropertiesManager.DebeziumConnectorType.MONGODB,
        emittedAt,
        false);

    // We can close the client after the initial snapshot is complete, incremental
    // iterator does not make use of the client.
    final AutoCloseableIterator<AirbyteMessage> initialSnapshotIterator = AutoCloseableIterators.appendOnClose(
        AutoCloseableIterators.concatWithEagerClose(initialSnapshotIterators), mongoClient::close);

    return List.of(initialSnapshotIterator, AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier, null));
  }

}
