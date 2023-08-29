/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.CHECKPOINT_INTERVAL;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.ID_FIELD;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.Projections;
import com.mongodb.client.model.Sorts;
import com.mongodb.connection.ClusterType;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStreamState;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.bson.BsonDocument;
import org.bson.conversions.Bson;
import org.bson.types.ObjectId;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoDbSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbSource.class);

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
    final var emittedAt = Instant.now();
    final var stateManager = MongoDbStateManager.createStateManager(state);
    final MongoClient mongoClient = MongoConnectionUtils.createMongoClient(config);

    try {
      final var database = mongoClient.getDatabase(databaseName);
      // TODO treat INCREMENTAL and FULL_REFRESH differently?
      return AutoCloseableIterators.appendOnClose(AutoCloseableIterators.concatWithEagerClose(
          convertCatalogToIterators(catalog, stateManager, database, emittedAt),
          AirbyteTraceMessageUtility::emitStreamStatusTrace),
          mongoClient::close);
    } catch (final Exception e) {
      mongoClient.close();
      throw e;
    }
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

          final var stateIterator = new MongoDbStateIterator(cursor, stateManager, airbyteStream, emittedAt, CHECKPOINT_INTERVAL);
          return AutoCloseableIterators.fromIterator(stateIterator, cursor::close, null);
        })
        .toList();
  }

  protected MongoClient createMongoClient(final JsonNode config) {
    return MongoConnectionUtils.createMongoClient(config);
  }

}
