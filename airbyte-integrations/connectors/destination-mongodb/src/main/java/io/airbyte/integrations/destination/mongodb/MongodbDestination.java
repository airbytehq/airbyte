/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static com.mongodb.client.model.Projections.excludeId;
import static io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.MongoCommandException;
import com.mongodb.MongoException;
import com.mongodb.MongoSecurityException;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.mongodb.MongoDatabase;
import io.airbyte.cdk.db.mongodb.MongoDatabaseException;
import io.airbyte.cdk.db.mongodb.MongoUtils;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;
import org.apache.commons.lang3.StringUtils;
import org.bson.Document;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongodbDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongodbDestination.class);

  private final MongodbNameTransformer namingResolver;

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new MongodbDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public MongodbDestination() {
    namingResolver = new MongodbNameTransformer();
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = sshWrappedDestination();
    LOGGER.info("starting destination: {}", MongodbDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MongodbDestination.class);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      final MongoDatabase database = getDatabase(config);
      final var databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
      final Set<String> databaseNames = getDatabaseNames(database);
      if (!databaseNames.contains(databaseName) && !databaseName.equals(database.getName())) {
        throw new MongoDatabaseException(databaseName);
      }
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final ConnectionErrorException e) {
      final String message = getErrorMessage(e.getStateCode(), e.getErrorCode(), e.getExceptionMessage(), e);
      AirbyteTraceMessageUtility.emitConfigErrorTrace(e, message);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage(message);
    } catch (final RuntimeException e) {
      LOGGER.error("Check failed.", e);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage(e.getMessage() != null ? e.getMessage() : e.toString());
    }
  }

  private Set<String> getDatabaseNames(final MongoDatabase mongoDatabase) {
    try {
      return MoreIterators.toSet(mongoDatabase.getDatabaseNames().iterator());
    } catch (final MongoSecurityException e) {
      final MongoCommandException exception = (MongoCommandException) e.getCause();
      throw new ConnectionErrorException(String.valueOf(exception.getCode()), e);
    } catch (final MongoException e) {
      throw new ConnectionErrorException(String.valueOf(e.getCode()), e);
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final MongoDatabase database = getDatabase(config);

    final Map<AirbyteStreamNameNamespacePair, MongodbWriteConfig> writeConfigs = new HashMap<>();
    for (final ConfiguredAirbyteStream configStream : catalog.getStreams()) {
      final AirbyteStream stream = configStream.getStream();
      final String streamName = stream.getName();
      final String collectionName = namingResolver.getRawTableName(streamName);
      final String tmpCollectionName = namingResolver.getTmpTableName(streamName);

      if (DestinationSyncMode.OVERWRITE == configStream.getDestinationSyncMode()) {
        database.getCollection(collectionName).drop();
      }

      final MongoCollection<Document> collection = database.getOrCreateNewCollection(tmpCollectionName);
      final Set<String> documentsHash = new HashSet<>();
      try (final MongoCursor<Document> cursor = collection.find().projection(excludeId()).iterator()) {
        while (cursor.hasNext()) {
          documentsHash.add(cursor.next().get(MongoUtils.AIRBYTE_DATA_HASH, String.class));
        }
      }

      writeConfigs.put(AirbyteStreamNameNamespacePair.fromAirbyteStream(stream),
          new MongodbWriteConfig(collectionName, tmpCollectionName, configStream.getDestinationSyncMode(), collection, documentsHash));
    }
    return new MongodbRecordConsumer(writeConfigs, database, catalog, outputRecordCollector);
  }

  /* Helpers */

  private MongoDatabase getDatabase(final JsonNode config) {
    return new MongoDatabase(getConnectionString(config), config.get(JdbcUtils.DATABASE_KEY).asText());
  }

  @VisibleForTesting
  String getConnectionString(final JsonNode config) {
    final var credentials = config.get(MongoUtils.AUTH_TYPE).get(MongoUtils.AUTHORIZATION).asText().equals(MongoUtils.LOGIN_AND_PASSWORD)
        ? String.format("%s:%s@", config.get(MongoUtils.AUTH_TYPE).get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(MongoUtils.AUTH_TYPE).get(JdbcUtils.PASSWORD_KEY).asText())
        : StringUtils.EMPTY;

    // backward compatibility check
    // the old mongo db spec only includes host, port, database, and auth_type
    // the new spec replaces host and port with the instance_type property
    if (config.has(MongoUtils.INSTANCE_TYPE)) {
      return buildConnectionString(config, credentials);
    } else {
      return String.format(MongoUtils.MONGODB_SERVER_URL, credentials, config.get(JdbcUtils.HOST_KEY).asText(),
          config.get(JdbcUtils.PORT_KEY).asText(), config.get(JdbcUtils.DATABASE_KEY).asText(), false);
    }
  }

  private String buildConnectionString(final JsonNode config, final String credentials) {
    final StringBuilder connectionStrBuilder = new StringBuilder();

    final JsonNode instanceConfig = config.get(MongoUtils.INSTANCE_TYPE);
    final var instance = MongoUtils.MongoInstanceType.fromValue(instanceConfig.get(MongoUtils.INSTANCE).asText());

    switch (instance) {
      case STANDALONE -> {
        // if there is no TLS present in spec, TLS should be enabled by default for strict encryption
        final var tls = !instanceConfig.has(JdbcUtils.TLS_KEY) || instanceConfig.get(JdbcUtils.TLS_KEY).asBoolean();
        connectionStrBuilder.append(
            String.format(MongoUtils.MONGODB_SERVER_URL, credentials, instanceConfig.get(JdbcUtils.HOST_KEY).asText(),
                instanceConfig.get(JdbcUtils.PORT_KEY).asText(),
                config.get(JdbcUtils.DATABASE_KEY).asText(), tls));
      }
      case REPLICA -> {
        connectionStrBuilder.append(
            String.format(MongoUtils.MONGODB_REPLICA_URL,
                credentials,
                instanceConfig.get(MongoUtils.SERVER_ADDRESSES).asText(),
                config.get(JdbcUtils.DATABASE_KEY).asText()));
        if (instanceConfig.has(MongoUtils.REPLICA_SET)) {
          connectionStrBuilder.append(String.format("&replicaSet=%s", instanceConfig.get(MongoUtils.REPLICA_SET).asText()));
        }
      }
      case ATLAS -> {
        connectionStrBuilder.append(
            String.format(MongoUtils.MONGODB_CLUSTER_URL, credentials,
                instanceConfig.get(MongoUtils.CLUSTER_URL).asText(),
                config.get(JdbcUtils.DATABASE_KEY).asText()));
      }
      default -> throw new IllegalArgumentException("Unsupported instance type: " + instance);
    }
    return connectionStrBuilder.toString();
  }

}
