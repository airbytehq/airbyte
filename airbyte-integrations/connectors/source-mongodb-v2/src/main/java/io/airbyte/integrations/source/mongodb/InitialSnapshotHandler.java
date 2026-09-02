/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.*;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIterator;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateEmitFrequency;
import io.airbyte.cdk.integrations.source.relationaldb.streamstatus.StreamStatusTraceEmitterIterator;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mongodb.MongoUtil.CollectionStatistics;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * Retrieves iterators used for the initial snapshot
 */
public class InitialSnapshotHandler {

  /**
   * For each given stream configured as incremental sync it will output an iterator that will
   * retrieve documents from the given database. Each iterator will start after the last checkpointed
   * document, if any, or from the beginning of the stream otherwise.
   */
  public List<AutoCloseableIterator<AirbyteMessage>> getIterators(
                                                                  final List<ConfiguredAirbyteStream> streams,
                                                                  final MongoDbStateManager stateManager,
                                                                  final MongoDatabase database,
                                                                  final MongoDbSourceConfig config,
                                                                  final boolean decorateWithStartedStatus,
                                                                  final boolean decorateWithCompletedStatus,
                                                                  final Instant emittedAt,
                                                                  final Optional<Duration> cdcInitialLoadTimeout) {
    final boolean isEnforceSchema = config.getEnforceSchema();
    final var checkpointInterval = config.getCheckpointInterval();

    return streams
        .stream()
        .filter(airbyteStream -> airbyteStream.getStream().getNamespace().equals(database.getName()))
        .map(airbyteStream -> {
          final var collectionName = airbyteStream.getStream().getName();
          final var namespace = airbyteStream.getStream().getNamespace();
          final var collection = database.getCollection(collectionName);
          final var fields = Projections.fields(Projections.include(CatalogHelpers.getTopLevelFieldNames(airbyteStream).stream().toList()));

          // find the existing state, if there is one, for this stream
          final Optional<MongoDbStreamState> existingState =
              stateManager.getStreamState(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());

          final Optional<CollectionStatistics> collectionStatistics = MongoUtil.getCollectionStatistics(database, airbyteStream);
          final var recordIterator = new MongoDbInitialLoadRecordIterator(collection, fields, existingState, isEnforceSchema,
              MongoUtil.getChunkSizeForCollection(collectionStatistics, airbyteStream), emittedAt, cdcInitialLoadTimeout);
          final var stateIterator =
              new SourceStateIterator<>(recordIterator, airbyteStream, stateManager, new StateEmitFrequency(checkpointInterval,
                  MongoConstants.CHECKPOINT_DURATION));
          final var iterator = AutoCloseableIterators.fromIterator(stateIterator, recordIterator::close, null);

          List<AutoCloseableIterator<AirbyteMessage>> itList = Stream.of(iterator).collect(Collectors.toList());
          if (decorateWithStartedStatus) {
            itList.addFirst(new StreamStatusTraceEmitterIterator(
                new AirbyteStreamStatusHolder(new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(collectionName, namespace),
                    AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED)));
          }

          if (decorateWithCompletedStatus) {
            itList.addLast(new StreamStatusTraceEmitterIterator(
                new AirbyteStreamStatusHolder(new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(collectionName, namespace),
                    AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE)));
          }
          return (itList.size() == 1) ? iterator : AutoCloseableIterators.concatWithEagerClose(itList);
        })
        .toList();
  }

}
