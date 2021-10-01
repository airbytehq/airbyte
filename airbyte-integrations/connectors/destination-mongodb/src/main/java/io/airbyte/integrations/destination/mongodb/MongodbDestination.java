/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static com.mongodb.client.model.Projections.excludeId;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.db.mongodb.MongoUtils.MongoInstanceType;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
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

  private static final String MONGODB_SERVER_URL = "mongodb://%s%s:%s/?authSource=%s&ssl=%s";
  private static final String MONGODB_CLUSTER_URL = "mongodb+srv://%s%s/%s?authSource=%s&retryWrites=true&w=majority&tls=true";
  private static final String MONGODB_REPLICA_URL = "mongodb://%s%s/%s?authSource=%s&directConnection=false&ssl=true";
  private static final String INSTANCE_TYPE = "instance_type";
  private static final String INSTANCE = "instance";
  private static final String CLUSTER_URL = "cluster_url";
  private static final String SERVER_ADDRESSES = "server_addresses";
  private static final String REPLICA_SET = "replica_set";
  private static final String TLS = "tls";
  private static final String HOST = "host";
  private static final String PORT = "port";
  private static final String DATABASE = "database";
  private static final String AUTH_TYPE = "auth_type";
  private static final String USERNAME = "username";
  private static final String PASSWORD = "password";
  private static final String AUTHORIZATION = "authorization";
  private static final String LOGIN_AND_PASSWORD = "login/password";
  private static final String AIRBYTE_DATA_HASH = "_airbyte_data_hash";

  private final MongodbNameTransformer namingResolver;

  public MongodbDestination() {
    namingResolver = new MongodbNameTransformer();
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new MongodbDestination();
    LOGGER.info("starting destination: {}", MongodbDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MongodbDestination.class);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try {
      var database = getDatabase(config);
      var databaseName = config.get(DATABASE).asText();
      Set<String> databaseNames = MoreIterators.toSet(database.getDatabaseNames().iterator());
      if (!databaseNames.contains(databaseName)) {
        throw new MongodbDatabaseException(databaseName);
      }
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (RuntimeException e) {
      LOGGER.error("Check failed.", e);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage(e.getMessage() != null ? e.getMessage() : e.toString());
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config,
                                            ConfiguredAirbyteCatalog catalog,
                                            Consumer<AirbyteMessage> outputRecordCollector) {
    var database = getDatabase(config);

    Map<AirbyteStreamNameNamespacePair, MongodbWriteConfig> writeConfigs = new HashMap<>();
    for (final ConfiguredAirbyteStream configStream : catalog.getStreams()) {
      final AirbyteStream stream = configStream.getStream();
      final String streamName = stream.getName();
      final String collectionName = namingResolver.getRawTableName(streamName);
      final String tmpCollectionName = namingResolver.getTmpTableName(streamName);

      if (DestinationSyncMode.OVERWRITE == configStream.getDestinationSyncMode()) {
        database.getCollection(collectionName).drop();
      }

      MongoCollection<Document> collection = database.getOrCreateNewCollection(tmpCollectionName);
      Set<String> documentsHash = new HashSet<>();
      try (MongoCursor<Document> cursor = collection.find().projection(excludeId()).iterator()) {
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

  private MongoDatabase getDatabase(JsonNode config) {
    return new MongoDatabase(getConnectionString(config), config.get(DATABASE).asText());
  }

  @VisibleForTesting
  String getConnectionString(JsonNode config) {
    var credentials = config.get(AUTH_TYPE).get(AUTHORIZATION).asText().equals(LOGIN_AND_PASSWORD)
        ? String.format("%s:%s@", config.get(AUTH_TYPE).get(USERNAME).asText(), config.get(AUTH_TYPE).get(PASSWORD).asText())
        : StringUtils.EMPTY;

    // backward compatibility check
    // the old mongo db spec only includes host, port, database, and auth_type
    // the new spec replaces host and port with the instance_type property
    if (config.has(INSTANCE_TYPE)) {
      return buildConnectionString(config, credentials);
    } else {
      return String.format(MONGODB_SERVER_URL, credentials, config.get(HOST).asText(),
          config.get(PORT).asText(), config.get(DATABASE).asText(), false);
    }
  }

  private String buildConnectionString(JsonNode config, String credentials) {
    StringBuilder connectionStrBuilder = new StringBuilder();

    JsonNode instanceConfig = config.get(INSTANCE_TYPE);
    MongoInstanceType instance = MongoInstanceType.fromValue(instanceConfig.get(INSTANCE).asText());

    switch (instance) {
      case STANDALONE -> {
        connectionStrBuilder.append(
            String.format(MONGODB_SERVER_URL, credentials, instanceConfig.get(HOST).asText(), instanceConfig.get(PORT).asText(),
                config.get(DATABASE).asText(), instanceConfig.get(TLS).asBoolean()));
      }
      case REPLICA -> {
        connectionStrBuilder.append(
            String.format(MONGODB_REPLICA_URL, credentials, instanceConfig.get(SERVER_ADDRESSES).asText(), config.get(DATABASE).asText(),
                config.get(DATABASE).asText()));
        if (instanceConfig.has(REPLICA_SET)) {
          connectionStrBuilder.append(String.format("&replicaSet=%s", instanceConfig.get(REPLICA_SET).asText()));
        }
      }
      case ATLAS -> {
        connectionStrBuilder.append(
            String.format(MONGODB_CLUSTER_URL, credentials, instanceConfig.get(CLUSTER_URL).asText(), config.get(DATABASE).asText(),
                config.get(DATABASE).asText()));
      }
      default -> throw new IllegalArgumentException("Unsupported instance type: " + instance);
    }
    return connectionStrBuilder.toString();
  }

}
