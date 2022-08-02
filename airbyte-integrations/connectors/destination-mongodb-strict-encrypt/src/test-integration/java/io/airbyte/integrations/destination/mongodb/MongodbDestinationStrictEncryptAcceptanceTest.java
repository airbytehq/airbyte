/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static com.mongodb.client.model.Projections.excludeId;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.client.MongoCursor;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.db.mongodb.MongoUtils.MongoInstanceType;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.bson.Document;
import org.junit.jupiter.api.BeforeAll;

public class MongodbDestinationStrictEncryptAcceptanceTest extends DestinationAcceptanceTest {

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  private static final String AUTH_TYPE = "auth_type";
  private static final String INSTANCE_TYPE = "instance_type";
  private static final String AIRBYTE_DATA = "_airbyte_data";

  private static JsonNode config;
  private static JsonNode failCheckConfig;

  private MongoDatabase mongoDatabase;
  private final MongodbNameTransformer namingResolver = new MongodbNameTransformer();

  @BeforeAll
  static void setupConfig() throws IOException {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a MongoDB credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }
    final String credentialsJsonString = Files.readString(CREDENTIALS_PATH);
    final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString);

    final JsonNode instanceConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance", MongoInstanceType.STANDALONE.getType())
        .put(JdbcUtils.HOST_KEY, credentialsJson.get(JdbcUtils.HOST_KEY).asText())
        .put(JdbcUtils.PORT_KEY, credentialsJson.get(JdbcUtils.PORT_KEY).asInt())
        .build());

    final JsonNode authConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("authorization", "login/password")
        .put(JdbcUtils.USERNAME_KEY, credentialsJson.get("user").asText())
        .put(JdbcUtils.PASSWORD_KEY, credentialsJson.get(JdbcUtils.PASSWORD_KEY).asText())
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.DATABASE_KEY, credentialsJson.get(JdbcUtils.DATABASE_KEY).asText())
        .put(AUTH_TYPE, authConfig)
        .put(INSTANCE_TYPE, instanceConfig)
        .build());

    failCheckConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.DATABASE_KEY, credentialsJson.get(JdbcUtils.DATABASE_KEY).asText())
        .put(AUTH_TYPE, Jsons.jsonNode(ImmutableMap.builder()
            .put("authorization", "none")
            .build()))
        .put(INSTANCE_TYPE, instanceConfig)
        .build());
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-mongodb-strict-encrypt:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.clone(config);
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.clone(failCheckConfig);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema) {
    final var collection = mongoDatabase.getOrCreateNewCollection(namingResolver.getRawTableName(streamName));
    final List<JsonNode> result = new ArrayList<>();
    try (final MongoCursor<Document> cursor = collection.find().projection(excludeId()).iterator()) {
      while (cursor.hasNext()) {
        result.add(Jsons.jsonNode(cursor.next().get(AIRBYTE_DATA)));
      }
    }
    return result;
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    final String connectionString = String.format("mongodb://%s:%s@%s:%s/%s?authSource=admin&ssl=true",
        config.get(AUTH_TYPE).get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(AUTH_TYPE).get(JdbcUtils.PASSWORD_KEY).asText(),
        config.get(INSTANCE_TYPE).get(JdbcUtils.HOST_KEY).asText(),
        config.get(INSTANCE_TYPE).get(JdbcUtils.PORT_KEY).asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText());

    mongoDatabase = new MongoDatabase(connectionString, config.get(JdbcUtils.DATABASE_KEY).asText());
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    for (final String collectionName : mongoDatabase.getCollectionNames()) {
      mongoDatabase.getDatabase().getCollection(collectionName).drop();
    }
    mongoDatabase.close();
  }

}
