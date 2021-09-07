/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.mongodb;

import static com.mongodb.client.model.Projections.excludeId;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.MongoClient;
import com.mongodb.MongoClientURI;
import com.mongodb.ServerAddress;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
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
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import javax.annotation.Nullable;
import org.bson.Document;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MongodbDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongodbDestination.class);

  private static final String MONGO_URI = "mongodb://%s:%s@%s:%s/?authSource=%s&authMechanism=SCRAM-SHA-1";
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
      var uri = getMongoClientURI(config);
      var client = getMongoClient(config.get(HOST).asText(), config.get(PORT).asInt(), uri);
      var database = getMongoDatabase(client, config.get(DATABASE).asText());
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
    var uri = getMongoClientURI(config);
    var client = getMongoClient(config.get(HOST).asText(), config.get(PORT).asInt(), uri);
    var database = getMongoDatabase(client, config.get(DATABASE).asText());

    Map<AirbyteStreamNameNamespacePair, MongodbWriteConfig> writeConfigs = new HashMap<>();
    for (final ConfiguredAirbyteStream configStream : catalog.getStreams()) {
      final AirbyteStream stream = configStream.getStream();
      final String streamName = stream.getName();
      final String collectionName = namingResolver.getRawTableName(streamName);
      final String tmpCollectionName = namingResolver.getTmpTableName(streamName);

      if (DestinationSyncMode.OVERWRITE == configStream.getDestinationSyncMode()) {
        database.getCollection(collectionName).drop();
      }

      MongoCollection<Document> collection = getOrCreateNewMongodbCollection(database, tmpCollectionName);
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

  private MongoClientURI getMongoClientURI(JsonNode config) {
    MongoClientURI uri = null;
    if (config.get(AUTH_TYPE).get(AUTHORIZATION).asText().equals(LOGIN_AND_PASSWORD)) {
      uri = new MongoClientURI(String.format(MONGO_URI, config.get(AUTH_TYPE).get(USERNAME).asText(),
          config.get(AUTH_TYPE).get(PASSWORD).asText(), config.get(HOST).asText(),
          config.get(PORT).asText(), config.get(DATABASE).asText()));
    }
    return uri;
  }

  private MongoClient getMongoClient(String host, int port, @Nullable MongoClientURI uri) {
    try {
      if (uri == null) {
        var serverAddress = new ServerAddress(host, port);
        return new MongoClient(serverAddress);
      } else {
        return new MongoClient(uri);
      }
    } catch (RuntimeException e) {
      throw new RuntimeException(e);
    }
  }

  private MongoDatabase getMongoDatabase(MongoClient mongoClient, String dataBaseName) {
    try {
      var databaseNames = StreamSupport
          .stream(mongoClient.listDatabaseNames().spliterator(), false)
          .collect(Collectors.toSet());
      if (!databaseNames.contains(dataBaseName)) {
        throw new MongodbDatabaseException(dataBaseName);
      }
      return mongoClient.getDatabase(dataBaseName);
    } catch (RuntimeException e) {
      throw new RuntimeException(e);
    }
  }

  private MongoCollection<Document> getOrCreateNewMongodbCollection(MongoDatabase database, String collectionName) {
    var collectionNames = StreamSupport
        .stream(database.listCollectionNames().spliterator(), false)
        .collect(Collectors.toSet());
    if (!collectionNames.contains(collectionName)) {
      database.createCollection(collectionName);
    }
    return database.getCollection(collectionName);
  }

}
