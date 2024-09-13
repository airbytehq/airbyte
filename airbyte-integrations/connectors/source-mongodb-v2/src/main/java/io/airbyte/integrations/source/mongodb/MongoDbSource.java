/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcInitialSnapshotUtils.validateStateSyncMode;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.MongoCommandException;
import com.mongodb.MongoSecurityException;
import com.mongodb.client.MongoClient;
import com.mongodb.connection.ClusterType;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcConnectorMetadataInjector;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcInitializer;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcState;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.protocol.models.v0.*;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
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
    AirbyteExceptionHandler.addThrowableForDeinterpolation(MongoCommandException.class);
    final Source source = new MongoDbSource();
    LOGGER.info("starting source: {}", MongoDbSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MongoDbSource.class);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final MongoDbSourceConfig sourceConfig = new MongoDbSourceConfig(config);
      try (final MongoClient mongoClient = createMongoClient(sourceConfig)) {
        final String databaseName = sourceConfig.getDatabaseName();
        if (MongoUtil.checkDatabaseExists(mongoClient, databaseName)) {
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
        } else {
          LOGGER.error("Unable to perform connection check.  Database '" + databaseName + "' does not exist.");
          return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED)
              .withMessage("Database does not exist.  Please check the source's configured database name.");
        }
      } catch (final MongoSecurityException e) {
        LOGGER.error("Unable to perform source check operation.", e);
        return new AirbyteConnectionStatus()
            .withMessage("Authentication failed.  Please check the source's configured credentials.")
            .withStatus(AirbyteConnectionStatus.Status.FAILED);
      } catch (final Exception e) {
        LOGGER.error("Unable to perform source check operation.", e);
        return new AirbyteConnectionStatus()
            .withMessage(e.getMessage())
            .withStatus(AirbyteConnectionStatus.Status.FAILED);
      }

      LOGGER.info("The source passed the check operation test!");
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final IllegalArgumentException e) {
      LOGGER.error("Unable to perform connection check operation.", e);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Unable to perform connection check operation: " + e.getMessage());
    }
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) {
    try {
      final MongoDbSourceConfig sourceConfig = new MongoDbSourceConfig(config);
      try (final MongoClient mongoClient = createMongoClient(sourceConfig)) {
        final String databaseName = sourceConfig.getDatabaseName();
        final Integer sampleSize = sourceConfig.getSampleSize();
        final boolean isSchemaEnforced = sourceConfig.getEnforceSchema();
        final List<AirbyteStream> streams = MongoUtil.getAirbyteStreams(mongoClient, databaseName, sampleSize, isSchemaEnforced);
        return new AirbyteCatalog().withStreams(streams);
      }
    } catch (final IllegalArgumentException e) {
      LOGGER.error("Unable to perform schema discovery operation.", e);
      throw e;
    }
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config,
                                                    final ConfiguredAirbyteCatalog catalog,
                                                    final JsonNode state) {
    final var emittedAt = Instant.now();
    final var cdcMetadataInjector = MongoDbCdcConnectorMetadataInjector.getInstance(emittedAt);
    final MongoDbSourceConfig sourceConfig = new MongoDbSourceConfig(config);
    final var stateManager = MongoDbStateManager.createStateManager(state, sourceConfig);

    if (catalog != null) {
      validateStateSyncMode(stateManager, catalog.getStreams());
      MongoUtil.checkSchemaModeMismatch(sourceConfig.getEnforceSchema(),
          stateManager.getCdcState() != null ? stateManager.getCdcState().schema_enforced() : sourceConfig.getEnforceSchema(), catalog);
    }

    try {
      // WARNING: do not close the client here since it needs to be used by the iterator
      final MongoClient mongoClient = createMongoClient(sourceConfig);
      try {
        final List<ConfiguredAirbyteStream> fullRefreshStreams =
            catalog.getStreams().stream().filter(s -> s.getSyncMode() == SyncMode.FULL_REFRESH).toList();
        final List<ConfiguredAirbyteStream> incrementalStreams = catalog.getStreams().stream().filter(s -> !fullRefreshStreams.contains(s)).toList();

        List<AutoCloseableIterator<AirbyteMessage>> iterators = new ArrayList<>();
        if (!fullRefreshStreams.isEmpty()) {
          LOGGER.info("There are {} Full refresh streams", fullRefreshStreams.size());
          iterators.addAll(createFullRefreshIterators(sourceConfig, mongoClient, fullRefreshStreams, stateManager, emittedAt));
        }

        if (!incrementalStreams.isEmpty()) {
          LOGGER.info("There are {} Incremental streams", incrementalStreams.size());
          iterators
              .addAll(cdcInitializer.createCdcIterators(mongoClient, cdcMetadataInjector, incrementalStreams, stateManager, emittedAt, sourceConfig));
        }
        return AutoCloseableIterators.concatWithEagerClose(iterators, AirbyteTraceMessageUtility::emitStreamStatusTrace);
      } catch (final Exception e) {
        mongoClient.close();
        throw e;
      }
    } catch (final Exception e) {
      LOGGER.error("Unable to perform sync read operation.", e);
      throw e;
    }
  }

  protected MongoClient createMongoClient(final MongoDbSourceConfig config) {
    return MongoConnectionUtils.createMongoClient(config);
  }

  List<AutoCloseableIterator<AirbyteMessage>> createFullRefreshIterators(final MongoDbSourceConfig sourceConfig,
                                                                         final MongoClient mongoClient,
                                                                         final List<ConfiguredAirbyteStream> streams,
                                                                         final MongoDbStateManager stateManager,
                                                                         final Instant emmitedAt) {
    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    if (stateManager.getCdcState() == null) {
      stateManager.updateCdcState(new MongoDbCdcState(null, sourceConfig.getEnforceSchema()));
    }
    final List<AutoCloseableIterator<AirbyteMessage>> fullRefreshIterators = initialSnapshotHandler.getIterators(
        streams,
        stateManager,
        mongoClient.getDatabase(sourceConfig.getDatabaseName()),
        sourceConfig,
        true,
        true,
        emmitedAt,
        Optional.empty());

    return fullRefreshIterators;
  }

}
