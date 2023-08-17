/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.FETCH_SIZE_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Projections;
import com.mongodb.client.model.Sorts;
import com.mongodb.connection.ClusterType;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.bson.BsonDocument;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.bson.types.ObjectId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoDbSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbSource.class);

  /** Helper class for holding a collection-name and stream state together */
  private record CollectionNameState(Optional<String> name, Optional<MongodbStreamState> state) {}

  /**
   * Number of documents to read at once.
   */
  private static final int BATCH_SIZE = 1000;

  public static void main(final String[] args) throws Exception {
    final Source source = new MongoDbSource();
    LOGGER.info("starting source: {}", MongoDbSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MongoDbSource.class);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try (final MongoClient mongoClient = createMongoClient(config)) {
      final String databaseName = config.get(DATABASE_CONFIGURATION_KEY).asText();

      /*
       * Perform the authorized collections check before the cluster type check. The MongoDB Java driver
       * needs to actually execute a command in order to fetch the cluster description. Querying for the
       * authorized collections guarantees that the cluster description will be available to the driver.
       */
      if (MongoUtil.getAuthorizedCollections(mongoClient, databaseName).isEmpty()) {
        return new AirbyteConnectionStatus()
            .withMessage("Target MongoDB database does not contain any authorized collections.")
            .withStatus(AirbyteConnectionStatus.Status.FAILED);
      }
      if (!ClusterType.REPLICA_SET.equals(mongoClient.getClusterDescription().getType())) {
        return new AirbyteConnectionStatus()
            .withMessage("Target MongoDB instance is not a replica set cluster.")
            .withStatus(AirbyteConnectionStatus.Status.FAILED);
      }
    } catch (final Exception e) {
      LOGGER.error("Unable to perform source check operation.", e);
      return new AirbyteConnectionStatus()
          .withMessage(e.getMessage())
          .withStatus(AirbyteConnectionStatus.Status.FAILED);
    }

    LOGGER.info("The source passed the check operation test!");
    return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) {
    try (final MongoClient mongoClient = createMongoClient(config)) {
      final String databaseName = config.get(DATABASE_CONFIGURATION_KEY).asText();
      final List<AirbyteStream> streams = MongoUtil.getAirbyteStreams(mongoClient, databaseName);
      return new AirbyteCatalog().withStreams(streams);
    }
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config,
                                                    final ConfiguredAirbyteCatalog catalog,
                                                    final JsonNode state) {
    final var databaseName = config.get(DATABASE_CONFIGURATION_KEY).asText();
    final var fetchSize = config.has(FETCH_SIZE_CONFIGURATION_KEY) ? config.get(FETCH_SIZE_CONFIGURATION_KEY).asInt() : BATCH_SIZE;
    final var emittedAt = Instant.now();

    final var states = convertState(state);
    //WARNING: do not close the client here since it needs to be used by the iterator
    final MongoClient mongoClient = createMongoClient(config);

    try {
      final var database = mongoClient.getDatabase(databaseName);
      return AutoCloseableIterators.appendOnClose(AutoCloseableIterators.concatWithEagerClose(
          convertCatalogToIterators(catalog, states, database, emittedAt, fetchSize),
          AirbyteTraceMessageUtility::emitStreamStatusTrace),
          mongoClient::close);
    } catch (final Exception e) {
      mongoClient.close();
      throw e;
    }
  }

  /**
   * Converts the JsonNode into a map of mongodb collection names to stream states.
   */
  @VisibleForTesting
  protected Map<String, MongodbStreamState> convertState(final JsonNode state) {
    // I'm unsure if the JsonNode data is going to be a singular AirbyteStateMessage or an array of
    // AirbyteStateMessages.
    // So this currently handles both cases, converting the singular message into a list of messages,
    // leaving the list of messages
    // as a list of messages, or returning an empty list.
    final List<AirbyteStateMessage> states = Jsons.tryObject(state, AirbyteStateMessage.class)
        .map(List::of)
        .orElseGet(() -> Jsons.tryObject(state, AirbyteStateMessage[].class)
            .map(Arrays::asList)
            .orElse(List.of()));

    // TODO add namespace support?
    return states.stream()
        .filter(s -> s.getType() == AirbyteStateType.STREAM)
        .map(s -> new CollectionNameState(
            Optional.ofNullable(s.getStream().getStreamDescriptor()).map(StreamDescriptor::getName),
            Jsons.tryObject(s.getStream().getStreamState(), MongodbStreamState.class)))
        // only keep states that could be parsed
        .filter(p -> p.name.isPresent() && p.state.isPresent())
        .collect(Collectors.toMap(
            p -> p.name.orElseThrow(),
            p -> p.state.orElseThrow()));
  }

  /**
   * Converts the streams in the catalog into a list of AutoCloseableIterators.
   */
  private List<AutoCloseableIterator<AirbyteMessage>> convertCatalogToIterators(
                                                                                final ConfiguredAirbyteCatalog catalog,
                                                                                final Map<String, MongodbStreamState> states,
                                                                                final MongoDatabase database,
                                                                                final Instant emittedAt,
                                                                                final Integer fetchSize) {
    return catalog.getStreams()
        .stream()
        .peek(airbyteStream -> {
          if (!airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL))
            LOGGER.warn("Stream {} configured with unsupported sync mode: {}", airbyteStream.getStream().getName(), airbyteStream.getSyncMode());
        })
        .filter(airbyteStream -> airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL))
        .map(airbyteStream -> {
          final var collectionName = airbyteStream.getStream().getName();
          // TODO verify that if all fields are selected that all fields are returned here
          // (or should this check and ignore them if all fields are selected)
          final var fields = Projections.fields(Projections.include(CatalogHelpers.getTopLevelFieldNames(airbyteStream).stream().toList()));
          final var cursor = getRecords(database, fields, collectionName, states, fetchSize);

          final var stateIterator = new MongoDbStateIterator(cursor, airbyteStream, emittedAt, fetchSize);
          return AutoCloseableIterators.fromIterator(stateIterator, cursor::close, null);
        })
        .toList();
  }

  protected MongoClient createMongoClient(final JsonNode config) {
    return MongoConnectionUtils.createMongoClient(config);
  }

  protected MongoCursor<Document> getRecords(
      final MongoDatabase database,
      final Bson fields,
      final String collectionName,
      final Map<String, MongodbStreamState> states,
      final Integer fetchSize) {

    final var collection = database.getCollection(collectionName);

    // The filter determines the starting point of this iterator based on the state of this collection.
    // If a state exists, it will use that state to create a query akin to "where _id > [last saved
    // state] order by _id ASC".
    // If no state exists, it will create a query akin to "where 1=1 order by _id ASC"
    final Bson filter = states.entrySet().stream()
        // look only for states that match this stream's name
        .filter(state -> state.getKey().equals(collectionName))
        .findFirst()
        // TODO add type support here when we add support for _id fields that are not ObjectId types
        .map(entry -> Filters.gt("_id", new ObjectId(entry.getValue().id())))
        // if nothing was found, return a new BsonDocument
        .orElseGet(BsonDocument::new);

    return collection.find()
        .filter(filter)
        .projection(fields)
        .sort(Sorts.ascending("_id"))
        .batchSize(fetchSize)
        .cursor();
  }
}
