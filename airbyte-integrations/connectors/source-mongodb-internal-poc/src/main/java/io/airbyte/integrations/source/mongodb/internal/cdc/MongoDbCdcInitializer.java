/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.CHECKPOINT_INTERVAL;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.CHECKPOINT_INTERVAL_CONFIGURATION_KEY;
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
import io.airbyte.integrations.debezium.internals.FirstRecordWaitTimeUtil;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbCdcTargetPosition;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumStateUtil;
import io.airbyte.integrations.source.mongodb.internal.InitialSnapshotHandler;
import io.airbyte.integrations.source.mongodb.internal.MongoUtil;
import io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.ExcludedField;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.time.Instant;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.Properties;
import java.util.Set;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
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
  private final MongoDbDebeziumFieldsUtil mongoDbDebeziumFieldsUtil;

  @VisibleForTesting
  MongoDbCdcInitializer(final MongoDbDebeziumStateUtil mongoDbDebeziumStateUtil, final MongoDbDebeziumFieldsUtil mongoDbDebeziumFieldsUtil) {
    this.mongoDbDebeziumStateUtil = mongoDbDebeziumStateUtil;
    this.mongoDbDebeziumFieldsUtil = mongoDbDebeziumFieldsUtil;
  }

  public MongoDbCdcInitializer() {
    this(new MongoDbDebeziumStateUtil(), new MongoDbDebeziumFieldsUtil());
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
                                                                        final JsonNode config) {

    final Duration firstRecordWaitTime = FirstRecordWaitTimeUtil.getFirstRecordWaitTime(config);
    final OptionalInt queueSize = MongoUtil.getDebeziumEventQueueSize(config);
    final String databaseName = config.get(DATABASE_CONFIGURATION_KEY).asText();
    // WARNING!!! debezium's mongodb connector doesn't let you specify a list of fields to
    // include, so we can't filter fields solely using the configured catalog. Instead,
    // debezium only lets you specify a list of fields to exclude. If the fields to exclude
    // we specify are not equal to all the fields in the source that are not in the
    // configured catalog then we will be outputting incorrect data.
    final Set<ExcludedField> fieldsNotIncludedInCatalog = mongoDbDebeziumFieldsUtil.getFieldsNotIncludedInCatalog(catalog, databaseName, mongoClient);
    final Properties defaultDebeziumProperties = MongoDbCdcProperties.getDebeziumProperties(fieldsNotIncludedInCatalog);
    final String replicaSet = config.get(REPLICA_SET_CONFIGURATION_KEY).asText();
    final JsonNode initialDebeziumState =
        mongoDbDebeziumStateUtil.constructInitialDebeziumState(mongoClient, MongoDbDebeziumPropertiesManager.normalizeName(databaseName), replicaSet);
    final JsonNode cdcState = (stateManager.getCdcState() == null || stateManager.getCdcState().state() == null) ? initialDebeziumState
        : Jsons.clone(stateManager.getCdcState().state());
    final Optional<BsonDocument> savedOffset = mongoDbDebeziumStateUtil.savedOffset(
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

    final boolean savedOffsetIsValid =
        savedOffset.filter(resumeToken -> mongoDbDebeziumStateUtil.isValidResumeToken(resumeToken, mongoClient)).isPresent();

    if (!savedOffsetIsValid) {
      LOGGER.warn("Saved offset is not valid. Airbyte will trigger a full refresh.");
      // If the offset in the state is invalid, reset the state to the initial state
      stateManager.resetState(Jsons.object(initialDebeziumState, MongoDbCdcState.class));
    } else {
      stateManager.updateCdcState(Jsons.object(cdcState, MongoDbCdcState.class));
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
            emittedAt, getCheckpointInterval(config));

    final AirbyteDebeziumHandler<BsonTimestamp> handler = new AirbyteDebeziumHandler<>(config,
        MongoDbCdcTargetPosition.targetPosition(mongoClient), false, firstRecordWaitTime, queueSize);
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

    return Stream
        .of(initialSnapshotIterators, Collections.singletonList(AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier, null)))
        .flatMap(Collection::stream)
        .collect(Collectors.toList());
  }

  private Integer getCheckpointInterval(final JsonNode config) {
    return config.get(CHECKPOINT_INTERVAL_CONFIGURATION_KEY) != null ? config.get(CHECKPOINT_INTERVAL_CONFIGURATION_KEY).asInt()
        : CHECKPOINT_INTERVAL;
  }

}
