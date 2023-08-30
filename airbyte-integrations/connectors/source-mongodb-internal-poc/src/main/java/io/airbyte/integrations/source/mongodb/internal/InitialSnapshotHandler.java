package io.airbyte.integrations.source.mongodb.internal;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.CHECKPOINT_DURATION;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.CHECKPOINT_INTERVAL;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.ID_FIELD;

import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Projections;
import com.mongodb.client.model.Sorts;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStreamState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.bson.BsonDocument;
import org.bson.conversions.Bson;
import org.bson.types.ObjectId;
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
      final Instant emittedAt) {
    return streams
        .stream()
        .peek(airbyteStream -> {
          if (!airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL))
            LOGGER.warn("Stream {} configured with unsupported sync mode: {}", airbyteStream.getStream().getName(), airbyteStream.getSyncMode());
        })
        .filter(airbyteStream -> airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL))
        .map(airbyteStream -> {
          final var collectionName = airbyteStream.getStream().getName();
          final var collection = database.getCollection(collectionName);
          final var fields = Projections.fields(Projections.include(CatalogHelpers.getTopLevelFieldNames(airbyteStream).stream().toList()));

          // find the existing state, if there is one, for this stream
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
