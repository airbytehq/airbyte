/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.REPLICA_SET_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.MongoClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbCdcTargetPosition;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumStateUtil;
import io.airbyte.integrations.source.mongodb.internal.InitialSnapshotHandler;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.time.Instant;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.OptionalInt;
import java.util.OptionalLong;
import java.util.Properties;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.bson.BsonTimestamp;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Provides methods to initialize the stream iterators based on the state of each stream in the
 * configured catalog.
 * <p />
 * <p />
 * For more information on the iterator selection logic, see
 * {@link MongoDbCdcInitialSnapshotUtils#getStreamsForInitialSnapshot(MongoDbStateManager, ConfiguredAirbyteCatalog, boolean)}
 * and {@link AirbyteDebeziumHandler#getIncrementalIterators}
 */
public class MongoDbCdcInitializer {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbCdcInitializer.class);

  private final MongoDbDebeziumStateUtil mongoDbDebeziumStateUtil;

  @VisibleForTesting
  MongoDbCdcInitializer(MongoDbDebeziumStateUtil mongoDbDebeziumStateUtil) {
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
                                                                        final ConfiguredAirbyteCatalog catalog,
                                                                        final MongoDbStateManager stateManager,
                                                                        final Instant emittedAt,
                                                                        final JsonNode config) {

    final Duration firstRecordWaitTime = Duration.ofMinutes(5); // TODO get from connector config?
    final OptionalInt queueSize = OptionalInt.empty(); // TODO get from connector config?
    final Properties defaultDebeziumProperties = MongoDbCdcProperties.getDebeziumProperties();
    final String databaseName = config.get(DATABASE_CONFIGURATION_KEY).asText();
    final String replicaSet = config.get(REPLICA_SET_CONFIGURATION_KEY).asText();
    final JsonNode initialDebeziumState = mongoDbDebeziumStateUtil.constructInitialDebeziumState(mongoClient, databaseName, replicaSet);
    final JsonNode cdcState = (stateManager.getCdcState() == null || stateManager.getCdcState().state() == null) ? initialDebeziumState
        : Jsons.clone(stateManager.getCdcState().state());
    final OptionalLong savedOffset = mongoDbDebeziumStateUtil.savedOffset(
        Jsons.clone(defaultDebeziumProperties),
        catalog,
        cdcState,
        config,
        mongoClient);

    // We should always be able to extract offset out of state if it's not null
    if (cdcState != null && savedOffset.isEmpty()) {
      throw new RuntimeException(
          "Unable extract the offset out of state, State mutation might not be working. " + cdcState);
    }

    final boolean savedOffsetAfterResumeToken = mongoDbDebeziumStateUtil.isSavedOffsetAfterResumeToken(mongoClient, savedOffset);

    if (!savedOffsetAfterResumeToken) {
      LOGGER.warn("Saved offset is before most recent resume token. Airbyte will trigger a full refresh.");
    }

    final MongoDbCdcState stateToBeUsed =
        (!savedOffsetAfterResumeToken || stateManager.getCdcState() == null || stateManager.getCdcState().state() == null)
            ? new MongoDbCdcState(initialDebeziumState)
            : stateManager.getCdcState();

    final List<ConfiguredAirbyteStream> initialSnapshotStreams =
        MongoDbCdcInitialSnapshotUtils.getStreamsForInitialSnapshot(stateManager, catalog, savedOffsetAfterResumeToken);
    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    final List<AutoCloseableIterator<AirbyteMessage>> initialSnapshotIterators =
        initialSnapshotHandler.getIterators(initialSnapshotStreams, stateManager, mongoClient.getDatabase(databaseName), emittedAt);

    final AirbyteDebeziumHandler<BsonTimestamp> handler = new AirbyteDebeziumHandler<>(config,
        MongoDbCdcTargetPosition.targetPosition(mongoClient), false, firstRecordWaitTime, queueSize);
    final MongoDbCdcStateHandler mongoDbCdcStateHandler = new MongoDbCdcStateHandler(stateManager);
    final MongoDbCdcConnectorMetadataInjector cdcMetadataInjector = MongoDbCdcConnectorMetadataInjector.getInstance(emittedAt);
    final MongoDbCdcSavedInfoFetcher cdcSavedInfoFetcher = new MongoDbCdcSavedInfoFetcher(stateToBeUsed);

    final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getMongoDbIncrementalIterator(catalog,
        cdcSavedInfoFetcher,
        mongoDbCdcStateHandler,
        cdcMetadataInjector,
        defaultDebeziumProperties,
        emittedAt,
        fieldsToExclude,
        false);

    return Stream
        .of(initialSnapshotIterators, Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier, null)))
        .flatMap(Collection::stream)
        .collect(Collectors.toList());
  }
}
