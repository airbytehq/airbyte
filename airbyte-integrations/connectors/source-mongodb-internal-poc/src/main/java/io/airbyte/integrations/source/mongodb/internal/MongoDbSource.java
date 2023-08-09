/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.DATABASE_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.MongoClient;
import com.mongodb.connection.ClusterType;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.List;
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
                                                    final JsonNode state)
      throws Exception {
    return null;
  }

  protected MongoClient createMongoClient(final JsonNode config) {
    return MongoConnectionUtils.createMongoClient(config);
  }

}
