/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.CHECKPOINT_DURATION;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.CHECKPOINT_INTERVAL;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.ID_FIELD;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.REPLICA_SET_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Projections;
import com.mongodb.client.model.Sorts;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbCdcTargetPosition;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumStateUtil;
import io.airbyte.integrations.source.mongodb.internal.MongoDbStateIterator;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStreamState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Duration;
import java.time.Instant;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.OptionalLong;
import java.util.Properties;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.bson.conversions.Bson;
import org.bson.types.ObjectId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoDbCdcInitializer {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbCdcInitializer.class);

  private final MongoDbDebeziumStateUtil mongoDbDebeziumStateUtil;

  public MongoDbCdcInitializer() {
    mongoDbDebeziumStateUtil = new MongoDbDebeziumStateUtil();
  }

  public List<AutoCloseableIterator<AirbyteMessage>> createCdcIterators(
                                                                        final MongoClient mongoClient,
                                                                        final ConfiguredAirbyteCatalog catalog,
                                                                        final MongoDbStateManager stateManager,
                                                                        final Instant emittedAt,
                                                                        final JsonNode config) {

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
        config);

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
    final List<AutoCloseableIterator<AirbyteMessage>> initialSnapshotIterators =
        convertCatalogToIterators(new ConfiguredAirbyteCatalog().withStreams(initialSnapshotStreams),
            stateManager, mongoClient.getDatabase(databaseName), emittedAt);

    final Duration firstRecordWaitTime = Duration.ofMinutes(5); // TODO get from connector config?
    final OptionalInt queueSize = OptionalInt.empty(); // TODO get from connector config?
    final AirbyteDebeziumHandler<BsonTimestamp> handler = new AirbyteDebeziumHandler<>(config,
        MongoDbCdcTargetPosition.targetPosition(mongoClient), false, firstRecordWaitTime, queueSize);
    final MongoDbCdcStateHandler mongoDbCdcStateHandler = new MongoDbCdcStateHandler(stateManager);
    final MongoDbCdcConnectorMetadataInjector cdcMetadataInjector = MongoDbCdcConnectorMetadataInjector.getInstance(emittedAt);
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

  /**
   * Converts the streams in the catalog into a list of AutoCloseableIterators.
   */
  private List<AutoCloseableIterator<AirbyteMessage>> convertCatalogToIterators(
                                                                                final ConfiguredAirbyteCatalog catalog,
                                                                                final MongoDbStateManager stateManager,
                                                                                final MongoDatabase database,
                                                                                final Instant emittedAt) {
    return catalog.getStreams()
        .stream()
        .peek(airbyteStream -> {
          if (!airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL))
            LOGGER.warn("Stream {} configured with unsupported sync mode: {}", airbyteStream.getStream().getName(), airbyteStream.getSyncMode());
        })
        .filter(airbyteStream -> airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL))
        .map(airbyteStream -> {
          final var collectionName = airbyteStream.getStream().getName();
          final var collection = database.getCollection(collectionName);
          // TODO verify that if all fields are selected that all fields are returned here
          // (or should this check and ignore them if all fields are selected)
          final var fields = Projections.fields(Projections.include(CatalogHelpers.getTopLevelFieldNames(airbyteStream).stream().toList()));

          // find the existing state, if there is one, for this steam
          final Optional<MongoDbStreamState> existingState =
              stateManager.getStreamState(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());

          // The filter determines the starting point of this iterator based on the state of this collection.
          // If a state exists, it will use that state to create a query akin to
          // "where _id > [last saved state] order by _id ASC".
          // If no state exists, it will create a query akin to "where 1=1 order by _id ASC"
          final Bson filter = existingState
              // TODO add type support here when we add support for _id fields that are not ObjectId types
              .map(state -> Filters.gt(ID_FIELD, new ObjectId(state.id())))
              // if nothing was found, return a new BsonDocument
              .orElseGet(BsonDocument::new);

          final var cursor = collection.find()
              .filter(filter)
              .projection(fields)
              .sort(Sorts.ascending(ID_FIELD))
              .cursor();

          final var stateIterator =
              new MongoDbStateIterator(cursor, stateManager, airbyteStream, emittedAt, CHECKPOINT_INTERVAL, CHECKPOINT_DURATION);
          return AutoCloseableIterators.fromIterator(stateIterator, cursor::close, null);
        })
        .toList();
  }

}
