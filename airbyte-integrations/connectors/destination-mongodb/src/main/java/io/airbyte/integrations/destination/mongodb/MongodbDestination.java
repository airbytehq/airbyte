/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static com.mongodb.client.model.Projections.excludeId;
import static io.airbyte.commons.exceptions.DisplayErrorMessage.getErrorMessage;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.MongoCommandException;
import com.mongodb.MongoException;
import com.mongodb.MongoSecurityException;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.db.mongodb.MongoUtils.MongoInstanceType;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.mongodb.exception.MongodbDatabaseException;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
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

  private static final String MONGODB_SERVER_URL = "mongodb://%s%s:%s/%s?authSource=admin&ssl=%s";
  private static final String MONGODB_CLUSTER_URL = "mongodb+srv://%s%s/%s?retryWrites=true&w=majority&tls=true";
  private static final String MONGODB_REPLICA_URL = "mongodb://%s%s/%s?authSource=admin&directConnection=false&ssl=true";
  private static final String INSTANCE_TYPE = "instance_type";
  private static final String INSTANCE = "instance";
  private static final String CLUSTER_URL = "cluster_url";
  private static final String SERVER_ADDRESSES = "server_addresses";
  private static final String REPLICA_SET = "replica_set";
  private static final String AUTH_TYPE = "auth_type";
  private static final String AUTHORIZATION = "authorization";
  private static final String LOGIN_AND_PASSWORD = "login/password";
  private static final String AIRBYTE_DATA_HASH = "_airbyte_data_hash";

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
        throw new MongodbDatabaseException(databaseName);
      }
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final ConfigErrorException e) {
      AirbyteTraceMessageUtility.emitConfigErrorTrace(e, e.getDisplayMessage());
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage(e.getDisplayMessage());
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
      throw new ConfigErrorException(getErrorMessage(
          String.valueOf(exception.getCode()), 0, null, exception), exception);
    } catch (final MongoException e) {
      throw new ConfigErrorException(getErrorMessage(
          String.valueOf(e.getCode()), 0, null, e), e);
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
          documentsHash.add(cursor.next().get(AIRBYTE_DATA_HASH, String.class));
        }
      }

      writeConfigs.put(AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream),
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
    final var credentials = config.get(AUTH_TYPE).get(AUTHORIZATION).asText().equals(LOGIN_AND_PASSWORD)
        ? String.format("%s:%s@", config.get(AUTH_TYPE).get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(AUTH_TYPE).get(JdbcUtils.PASSWORD_KEY).asText())
        : StringUtils.EMPTY;

    // backward compatibility check
    // the old mongo db spec only includes host, port, database, and auth_type
    // the new spec replaces host and port with the instance_type property
    if (config.has(INSTANCE_TYPE)) {
      return buildConnectionString(config, credentials);
    } else {
      return String.format(MONGODB_SERVER_URL, credentials, config.get(JdbcUtils.HOST_KEY).asText(),
          config.get(JdbcUtils.PORT_KEY).asText(), config.get(JdbcUtils.DATABASE_KEY).asText(), false);
    }
  }

  private String buildConnectionString(final JsonNode config, final String credentials) {
    final StringBuilder connectionStrBuilder = new StringBuilder();

    final JsonNode instanceConfig = config.get(INSTANCE_TYPE);
    final MongoInstanceType instance = MongoInstanceType.fromValue(instanceConfig.get(INSTANCE).asText());

    switch (instance) {
      case STANDALONE -> {
        // if there is no TLS present in spec, TLS should be enabled by default for strict encryption
        final var tls = !instanceConfig.has(JdbcUtils.TLS_KEY) || instanceConfig.get(JdbcUtils.TLS_KEY).asBoolean();
        connectionStrBuilder.append(
            String.format(MONGODB_SERVER_URL, credentials, instanceConfig.get(JdbcUtils.HOST_KEY).asText(),
                instanceConfig.get(JdbcUtils.PORT_KEY).asText(),
                config.get(JdbcUtils.DATABASE_KEY).asText(), tls));
      }
      case REPLICA -> {
        connectionStrBuilder.append(
            String.format(MONGODB_REPLICA_URL, credentials, instanceConfig.get(SERVER_ADDRESSES).asText(),
                config.get(JdbcUtils.DATABASE_KEY).asText()));
        if (instanceConfig.has(REPLICA_SET)) {
          connectionStrBuilder.append(String.format("&replicaSet=%s", instanceConfig.get(REPLICA_SET).asText()));
        }
      }
      case ATLAS -> {
        connectionStrBuilder.append(
            String.format(MONGODB_CLUSTER_URL, credentials, instanceConfig.get(CLUSTER_URL).asText(), config.get(JdbcUtils.DATABASE_KEY).asText()));
      }
      default -> throw new IllegalArgumentException("Unsupported instance type: " + instance);
    }
    return connectionStrBuilder.toString();
  }

}
