/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.DATABASE_CONFIGURATION_KEY;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.MongoClient;
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
import io.airbyte.protocol.models.v0.AirbyteStreamState;
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
import org.bson.conversions.Bson;
import org.bson.types.ObjectId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoDbSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbSource.class);
  private record Pair(Optional<String> name, Optional<MongodbStreamState> state){}

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
                                                    final JsonNode state)
      throws Exception {
    LOGGER.info("state is {}", state);

    final var databaseName = config.get(DATABASE_CONFIGURATION_KEY).asText();
    LOGGER.info("database is {}", databaseName);
    LOGGER.info("catalog is {}", catalog);
    final var emittedAt = Instant.now();

    final var states = convertState(state);
    LOGGER.info("converted state is {}", states);

    try (final MongoClient mongoClient = MongoConnectionUtils.createMongoClient(config)) {
      final var database = mongoClient.getDatabase(databaseName);

      final List<AutoCloseableIterator<AirbyteMessage>> incIters = incrIters(database, catalog, states, emittedAt);

      return AutoCloseableIterators.appendOnClose(AutoCloseableIterators.concatWithEagerClose(incIters, AirbyteTraceMessageUtility::emitStreamStatusTrace), ()-> {
      });
    }
  }

  @VisibleForTesting
  protected Map<String, MongodbStreamState> convertState(final JsonNode state) {
    // unsure if these will or will not be a list of AirbyteStreamStates, so I handle both cases
    final List<AirbyteStateMessage> states = Jsons.tryObject(state, AirbyteStateMessage.class)
        .map(List::of)
        .orElseGet(() ->
            Jsons.tryObject(state, AirbyteStateMessage[].class)
                .map(Arrays::asList)
                .orElse(List.of())
        );

    // TODO add namespace support?
    return states.stream()
        .filter(s -> s.getType() == AirbyteStateType.STREAM)
        .map(s -> new Pair(
            Optional.ofNullable(s.getStream().getStreamDescriptor()).map(StreamDescriptor::getName),
            Jsons.tryObject(s.getStream().getStreamState(), MongodbStreamState.class))
        )
        // only keep states that could be parsed
        .filter(p -> p.name.isPresent() && p.state.isPresent())
        .collect(Collectors.toMap(
          p -> p.name.orElseThrow(),
          p -> p.state.orElseThrow())
        );
  }

  private List<AutoCloseableIterator<AirbyteMessage>> incrIters(final MongoDatabase database, final ConfiguredAirbyteCatalog catalog, final Map<String, MongodbStreamState> states, final Instant emittedAt) {
    return catalog.getStreams()
        .stream()
        .filter(airbyteStream -> airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL))
        .map(airbyteStream -> {
          // the stream name is in the format of "[database].[collection]" and we only need the collection.
          final var collectionName = airbyteStream.getStream().getName().split("\\.", 2)[1];
          LOGGER.info("collection is {}", collectionName);
          final var collection = database.getCollection(collectionName);
          // TODO verify that if all fields are selected that all fields are returned here
          //  (or should this check and ignore them if all fields are selected)
          final var fields = Projections.fields(Projections.include(CatalogHelpers.getTopLevelFieldNames(airbyteStream).stream().toList()));
          LOGGER.info("fields are {}", fields);


          final Bson filter;
          if (states.containsKey(airbyteStream.getStream().getName())) {
            filter = Filters.gt("_id", new ObjectId(states.get(airbyteStream.getStream().getName()).id()));
          } else {
            filter = new BsonDocument();
          }

          LOGGER.info("filter is {}", filter);

          final var cursor = collection.find()
              .filter(filter)
              .projection(fields)
              .sort(Sorts.ascending("_id"))
              .batchSize(BATCH_SIZE)
              .cursor();

          final var closeableIterator = AutoCloseableIterators.fromIterator(new MongoDbStateIterator(cursor, airbyteStream, emittedAt, BATCH_SIZE));
          return AutoCloseableIterators.appendOnClose(closeableIterator, cursor::close);
        })
        .toList();
  }

  protected MongoClient createMongoClient(final JsonNode config) {
    return MongoConnectionUtils.createMongoClient(config);
  }

}
