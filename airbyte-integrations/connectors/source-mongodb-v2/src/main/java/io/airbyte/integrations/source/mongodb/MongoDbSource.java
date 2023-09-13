/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIG_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.MongoClient;
import com.mongodb.connection.ClusterType;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcConnectorMetadataInjector;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcInitializer;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.protocol.models.v0.*;
import java.time.Instant;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongoDbSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbSource.class);

  private final MongoDbCdcInitializer cdcInitializer;

  public MongoDbSource() {
    this(new MongoDbCdcInitializer());
  }

  @VisibleForTesting
  MongoDbSource(final MongoDbCdcInitializer cdcInitializer) {
    this.cdcInitializer = cdcInitializer;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = new MongoDbSource();
    LOGGER.info("starting source: {}", MongoDbSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MongoDbSource.class);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    if (config.has(DATABASE_CONFIG_CONFIGURATION_KEY)) {
      final JsonNode databaseConfig = config.get(DATABASE_CONFIG_CONFIGURATION_KEY);
      try (final MongoClient mongoClient = createMongoClient(databaseConfig)) {
        final String databaseName = databaseConfig.get(DATABASE_CONFIGURATION_KEY).asText();

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
          LOGGER.error("Target MongoDB instance is not a replica set cluster.");
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
    } else {
      LOGGER
          .error("Unable to perform connection check.  Configuration is missing required '" + DATABASE_CONFIG_CONFIGURATION_KEY + "' configuration.");
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Database connection configuration missing.");
    }
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) {
    if (config.has(DATABASE_CONFIG_CONFIGURATION_KEY)) {
      final JsonNode databaseConfig = config.get(DATABASE_CONFIG_CONFIGURATION_KEY);
      try (final MongoClient mongoClient = createMongoClient(databaseConfig)) {
        final String databaseName = databaseConfig.get(DATABASE_CONFIGURATION_KEY).asText();
        final List<AirbyteStream> streams = MongoUtil.getAirbyteStreams(mongoClient, databaseName);
        return new AirbyteCatalog().withStreams(streams);
      }
    } else {
      LOGGER
          .error("Unable to perform schema discovery.  Configuration is missing required '" + DATABASE_CONFIG_CONFIGURATION_KEY + "' configuration.");
      throw new IllegalArgumentException("Database connection configuration missing.");
    }
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config,
                                                    final ConfiguredAirbyteCatalog catalog,
                                                    final JsonNode state) {
    final var emittedAt = Instant.now();
    final var cdcMetadataInjector = MongoDbCdcConnectorMetadataInjector.getInstance(emittedAt);
    final var stateManager = MongoDbStateManager.createStateManager(state);

    if (config.has(DATABASE_CONFIG_CONFIGURATION_KEY)) {
      final JsonNode databaseConfig = config.get(DATABASE_CONFIG_CONFIGURATION_KEY);

      // WARNING: do not close the client here since it needs to be used by the iterator
      final MongoClient mongoClient = createMongoClient(databaseConfig);

      try {
        final var iteratorList =
            cdcInitializer.createCdcIterators(mongoClient, cdcMetadataInjector, catalog, stateManager, emittedAt, databaseConfig);
        return AutoCloseableIterators.concatWithEagerClose(iteratorList, AirbyteTraceMessageUtility::emitStreamStatusTrace);
      } catch (final Exception e) {
        mongoClient.close();
        throw e;
      }
    } else {
      LOGGER.error("Unable to perform sync.  Configuration is missing required '" + DATABASE_CONFIG_CONFIGURATION_KEY + "' configuration.");
      throw new IllegalArgumentException("Database connection configuration missing.");
    }
  }

  protected MongoClient createMongoClient(final JsonNode config) {
    return MongoConnectionUtils.createMongoClient(config);
  }

}
