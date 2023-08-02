/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.PASSWORD_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.REPLICA_SET_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.USER_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.ConnectionString;
import com.mongodb.MongoClientSettings;
import com.mongodb.MongoCredential;
import com.mongodb.MongoDriverInformation;
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
    final String authSource = config.get(AUTH_SOURCE_CONFIGURATION_KEY).asText();
    final String connectionString = config.get(CONNECTION_STRING_CONFIGURATION_KEY).asText();
    final String replicaSet = config.get(REPLICA_SET_CONFIGURATION_KEY).asText();

    final ConnectionString mongoConnectionString = new ConnectionString(connectionString + "?replicaSet=" +
        replicaSet + "&retryWrites=false&provider=airbyte&tls=true");

    final MongoDriverInformation mongoDriverInformation = MongoDriverInformation.builder()
        .driverName("Airbyte")
        .build();

    final MongoClientSettings.Builder mongoClientSettingsBuilder = MongoClientSettings.builder()
        .applyConnectionString(mongoConnectionString)
        .readPreference(ReadPreference.secondaryPreferred());

    if (config.has(USER_CONFIGURATION_KEY) && config.has(PASSWORD_CONFIGURATION_KEY)) {
      final String user = config.get(USER_CONFIGURATION_KEY).asText();
      final String password = config.get(PASSWORD_CONFIGURATION_KEY).asText();
      mongoClientSettingsBuilder.credential(MongoCredential.createCredential(user, authSource, password.toCharArray()));
    }

    return MongoClients.create(mongoClientSettingsBuilder.build(), mongoDriverInformation);
  }

}
