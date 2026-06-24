/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcInitialSnapshotUtils.validateStateSyncMode;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.MongoCommandException;
import com.mongodb.MongoSecurityException;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import com.mongodb.connection.ClusterType;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.commons.exceptions.ConfigErrorException;
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
import org.bson.BsonDocument;
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
        final List<String> databaseNames = sourceConfig.getDatabaseNames();

        if (databaseNames.isEmpty()) {
          return new AirbyteConnectionStatus()
              .withMessage("No databases specified in the configuration.")
              .withStatus(AirbyteConnectionStatus.Status.FAILED);
        }

        /*
         * Perform the authorized collections check before the cluster type check. The MongoDB Java driver
         * needs to actually execute a command in order to fetch the cluster description. Querying for the
         * authorized collections guarantees that the cluster description will be available to the driver.
         */
        boolean hasAuthorizedCollections = false;
        List<String> databasesWithoutPermission = new ArrayList<>();

        for (String databaseName : databaseNames) {
          if (!MongoUtil.getAuthorizedCollections(mongoClient, databaseName).isEmpty()) {
            hasAuthorizedCollections = true;
            LOGGER.info("Found authorized collections in database: {}", databaseName);
          } else {
            databasesWithoutPermission.add(databaseName);
            LOGGER.warn("No authorized collections found in database: {}", databaseName);
          }
        }

        if (!databasesWithoutPermission.isEmpty()) {
          LOGGER.warn("The following databases have no authorized collections: {}", String.join(", ", databasesWithoutPermission));
        }

        if (!hasAuthorizedCollections) {
          return new AirbyteConnectionStatus()
              .withMessage("Target MongoDB databases do not contain any authorized collections. Databases without permissions: "
                  + String.join(", ", databasesWithoutPermission))
              .withStatus(AirbyteConnectionStatus.Status.FAILED);
        }

        if (!ClusterType.REPLICA_SET.equals(mongoClient.getClusterDescription().getType())) {
          LOGGER.error("Target MongoDB instance is not a replica set cluster.");
          return new AirbyteConnectionStatus()
              .withMessage("Target MongoDB instance is not a replica set cluster.")
              .withStatus(AirbyteConnectionStatus.Status.FAILED);
        }

        /*
         * Probe the {@code changeStream} privilege on the configured databases. The authorized collections
         * check above only requires the {@code listCollections} privilege, which means a misconfigured role
         * can pass CHECK and only fail later on the first incremental sync. We open (and immediately close)
         * a change stream cursor so that a missing privilege surfaces as a clear configuration failure at
         * "Test connection" time.
         */
        final Optional<AirbyteConnectionStatus> changeStreamProbeFailure = probeChangeStreamPrivilege(mongoClient, databaseNames);
        if (changeStreamProbeFailure.isPresent()) {
          return changeStreamProbeFailure.get();
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
        final List<String> databaseNames = sourceConfig.getDatabaseNames();
        final Integer sampleSize = sourceConfig.getSampleSize();
        final boolean isSchemaEnforced = sourceConfig.getEnforceSchema();
        final Integer discoverTimeout = sourceConfig.getStreamDiscoveryTimeoutSeconds();

        List<AirbyteStream> allStreams = new ArrayList<>();
        for (String databaseName : databaseNames) {
          LOGGER.info("Discovering collections in database: {}", databaseName);
          List<AirbyteStream> streams = MongoUtil.getAirbyteStreams(mongoClient, databaseName, sampleSize, isSchemaEnforced, discoverTimeout);
          allStreams.addAll(streams);
        }

        return new AirbyteCatalog().withStreams(allStreams);
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
        final AutoCloseableIterator<AirbyteMessage> baseIterator =
            AutoCloseableIterators.concatWithEagerClose(iterators, AirbyteTraceMessageUtility::emitStreamStatusTrace);
        // Wrap the iterator to catch BSONObjectTooLarge errors and provide helpful error messages
        return wrapIteratorWithBsonErrorHandling(baseIterator);
      } catch (final Exception e) {
        mongoClient.close();
        throw e;
      }
    } catch (final Exception e) {
      LOGGER.error("Unable to perform sync read operation.", e);
      if (MongoUtil.isUnauthorizedException(e)) {
        throw new ConfigErrorException(
            MongoUtil.buildChangeStreamUnauthorizedMessage(sourceConfig.getDatabaseNames()),
            e,
            MongoUtil.findUnauthorizedException(e).map(Throwable::getMessage).orElse(""));
      }
      throw e;
    }
  }

  /**
   * Opens (and immediately closes) a change stream cursor against each configured database to verify
   * that the configured MongoDB user has the {@code find} and {@code changeStream} privileges
   * required for incremental / CDC syncs. If any database is missing the privilege, returns a
   * {@code FAILED} status with the same actionable message that {@link MongoDbSource#read} surfaces
   * at sync time, so users see the misconfiguration at "Test connection" time instead of on the first
   * sync.
   *
   * <p>
   * Any other exception (including {@link MongoCommandException}s with a different error code) is
   * rethrown so that the existing error-handling fallthrough in {@link #check} continues to apply.
   */
  private Optional<AirbyteConnectionStatus> probeChangeStreamPrivilege(final MongoClient mongoClient,
                                                                       final List<String> databaseNames) {
    for (final String databaseName : databaseNames) {
      final ChangeStreamIterable<BsonDocument> probeStream = mongoClient.getDatabase(databaseName).watch(BsonDocument.class);
      try (final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> cursor = probeStream.cursor()) {
        cursor.tryNext();
      } catch (final RuntimeException e) {
        if (MongoUtil.isUnauthorizedException(e)) {
          final String message = MongoUtil.buildChangeStreamUnauthorizedMessage(List.of(databaseName));
          LOGGER.error("MongoDB user is not authorized to open a change stream on database {}. "
              + "Underlying server response: {}", databaseName,
              MongoUtil.findUnauthorizedException(e).map(Throwable::getMessage).orElse(e.getMessage()));
          return Optional.of(new AirbyteConnectionStatus()
              .withMessage(message)
              .withStatus(AirbyteConnectionStatus.Status.FAILED));
        }
        throw e;
      }
    }
    return Optional.empty();
  }

  /**
   * Wraps an iterator to catch BSONObjectTooLarge errors during CDC operations and provide helpful,
   * actionable error messages to users.
   *
   * @param iterator The base iterator to wrap.
   * @return A wrapped iterator that catches BSONObjectTooLarge errors.
   */
  private AutoCloseableIterator<AirbyteMessage> wrapIteratorWithBsonErrorHandling(
                                                                                  final AutoCloseableIterator<AirbyteMessage> iterator) {
    return new AutoCloseableIterator<>() {

      @Override
      public boolean hasNext() {
        try {
          return iterator.hasNext();
        } catch (final Exception e) {
          throw handlePotentialBsonTooLargeError(e);
        }
      }

      @Override
      public AirbyteMessage next() {
        try {
          return iterator.next();
        } catch (final Exception e) {
          throw handlePotentialBsonTooLargeError(e);
        }
      }

      @Override
      public void close() throws Exception {
        iterator.close();
      }

      private RuntimeException handlePotentialBsonTooLargeError(final Exception e) {
        if (MongoUtil.isBsonObjectTooLargeException(e)) {
          LOGGER.error("BSONObjectTooLarge error detected during CDC sync. Original error: {}", e.getMessage(), e);
          throw new ConfigErrorException(MongoConstants.BSON_OBJECT_TOO_LARGE_ERROR_MESSAGE, e);
        }
        if (e instanceof RuntimeException) {
          throw (RuntimeException) e;
        }
        throw new RuntimeException(e);
      }

    };
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

    final List<AutoCloseableIterator<AirbyteMessage>> fullRefreshIterators = new ArrayList<>();

    for (String databaseName : sourceConfig.getDatabaseNames()) {
      List<ConfiguredAirbyteStream> databaseStreams = streams.stream()
          .filter(stream -> stream.getStream().getNamespace().equals(databaseName))
          .toList();
      if (!databaseStreams.isEmpty()) {
        LOGGER.info("Processing full refresh for database: {} with {} streams", databaseName, databaseStreams.size());
        fullRefreshIterators.addAll(initialSnapshotHandler.getIterators(
            databaseStreams,
            stateManager,
            mongoClient.getDatabase(databaseName),
            sourceConfig,
            true,
            true,
            emmitedAt,
            Optional.empty()));
      }
    }

    return fullRefreshIterators;
  }

}
