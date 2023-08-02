/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.ConnectionString;
import com.mongodb.MongoClientSettings;
import com.mongodb.MongoCredential;
import com.mongodb.ReadPreference;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;

/**
 * Helper utility for building a {@link MongoClient}.
 */
public class MongoConnectionUtils {

  /**
   * Creates a new {@link MongoClient} from the source configuration.
   *
   * @param config The source's configuration.
   * @return The configured {@link MongoClient}.
   */
  public static MongoClient createMongoClient(final JsonNode config) {
    final String authSource = config.get("auth_source").asText();
    final String connectionString = config.get("connection_string").asText();
    final String replicaSet = config.get("replica_set").asText();

    final ConnectionString mongoConnectionString = new ConnectionString(connectionString + "?replicaSet=" +
        replicaSet + "&retryWrites=false&provider=airbyte&tls=true");

    final MongoClientSettings.Builder mongoClientSettingsBuilder = MongoClientSettings.builder()
        .applyConnectionString(mongoConnectionString)
        .readPreference(ReadPreference.secondaryPreferred());

    if (config.has("user") && config.has("password")) {
      final String user = config.get("user").asText();
      final String password = config.get("password").asText();
      mongoClientSettingsBuilder.credential(MongoCredential.createCredential(user, authSource, password.toCharArray()));
    }

    return MongoClients.create(mongoClientSettingsBuilder.build());
  }

}
