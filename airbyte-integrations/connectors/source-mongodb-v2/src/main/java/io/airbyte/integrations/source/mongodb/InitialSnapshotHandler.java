/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.*;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIterator;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateEmitFrequency;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mongodb.MongoUtil.CollectionStatistics;
import io.airbyte.integrations.source.mongodb.state.IdType;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.bson.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Retrieves iterators used for the initial snapshot
 */
public class InitialSnapshotHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(InitialSnapshotHandler.class);

  /**
   * For each given stream configured as incremental sync it will output an iterator that will
   * retrieve documents from the given database. Each iterator will start after the last checkpointed
   * document, if any, or from the beginning of the stream otherwise.
   */
  public List<AutoCloseableIterator<AirbyteMessage>> getIterators(
                                                                  final List<ConfiguredAirbyteStream> streams,
                                                                  final MongoDbStateManager stateManager,
                                                                  final MongoDatabase database,
                                                                  final MongoDbSourceConfig config) {
    final boolean isEnforceSchema = config.getEnforceSchema();
    final var checkpointInterval = config.getCheckpointInterval();
    return streams
        .stream()
        .map(airbyteStream -> {
          final var collectionName = airbyteStream.getStream().getName();
          final var collection = database.getCollection(collectionName);
          final var fields = Projections.fields(Projections.include(CatalogHelpers.getTopLevelFieldNames(airbyteStream).stream().toList()));

          final var idTypes = aggregateIdField(collection);
          if (idTypes.size() > 1) {
            throw new ConfigErrorException("The _id fields in a collection must be consistently typed (collection = " + collectionName + ").");
          }

          idTypes.stream().findFirst().ifPresent(idType -> {
            if (IdType.findByBsonType(idType).isEmpty()) {
              throw new ConfigErrorException("Only _id fields with the following types are currently supported: " + IdType.SUPPORTED
                  + " (collection = " + collectionName + ").");
            }
          });

          // find the existing state, if there is one, for this stream
          final Optional<MongoDbStreamState> existingState =
              stateManager.getStreamState(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());

          final Optional<CollectionStatistics> collectionStatistics = MongoUtil.getCollectionStatistics(database, airbyteStream);
          final var recordIterator = new MongoDbInitialLoadRecordIterator(collection, fields, existingState, isEnforceSchema,
              MongoUtil.getChunkSizeForCollection(collectionStatistics, airbyteStream));
          final var stateIterator =
              new SourceStateIterator<>(recordIterator, airbyteStream, stateManager, new StateEmitFrequency(checkpointInterval,
                  MongoConstants.CHECKPOINT_DURATION));
          return AutoCloseableIterators.fromIterator(stateIterator, recordIterator::close, null);
        })
        .toList();
  }

  /**
   * Returns a list of types (as strings) that the _id field has for the provided collection.
   *
   * @param collection Collection to aggregate the _id types of.
   * @return List of bson types (as strings) that the _id field contains.
   */
  private List<String> aggregateIdField(final MongoCollection<Document> collection) {
    final List<String> idTypes = new ArrayList<>();
    /*
     * Sanity check that all ID_FIELD values are of the same type for this collection.
     * db.collection.aggregate([{ $group : { _id : { $type : "$_id" }, count : { $sum : 1 } } }])
     */
    collection.aggregate(List.of(
        Aggregates.group(
            new Document(MongoConstants.ID_FIELD, new Document("$type", "$_id")),
            Accumulators.sum("count", 1))))
        .forEach(document -> {
          // the document will be in the structure of
          // {"_id": {"_id": "[TYPE]"}, "count": [COUNT]}
          // where [TYPE] is the bson type (objectId, string, etc.) and [COUNT] is the number of documents of
          // that type
          final Document innerDocument = document.get(MongoConstants.ID_FIELD, Document.class);
          idTypes.add(innerDocument.get(MongoConstants.ID_FIELD).toString());
        });

    return idTypes;
  }

}
