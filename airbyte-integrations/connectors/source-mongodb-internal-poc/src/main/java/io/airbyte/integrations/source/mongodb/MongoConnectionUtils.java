/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DRIVER_NAME;
import static io.airbyte.integrations.source.mongodb.MongoConstants.PASSWORD_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.USER_CONFIGURATION_KEY;

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
    final ConnectionString mongoConnectionString = new ConnectionString(buildConnectionString(config));

    final MongoDriverInformation mongoDriverInformation = MongoDriverInformation.builder()
        .driverName(DRIVER_NAME)
        .build();

    final MongoClientSettings.Builder mongoClientSettingsBuilder = MongoClientSettings.builder()
        .applyConnectionString(mongoConnectionString)
        .readPreference(ReadPreference.secondaryPreferred());

    if (config.has(USER_CONFIGURATION_KEY) && config.has(PASSWORD_CONFIGURATION_KEY)) {
      final String authSource = config.get(AUTH_SOURCE_CONFIGURATION_KEY).asText();
      final String user = config.get(USER_CONFIGURATION_KEY).asText();
      final String password = config.get(PASSWORD_CONFIGURATION_KEY).asText();
      mongoClientSettingsBuilder.credential(MongoCredential.createCredential(user, authSource, password.toCharArray()));
    }

    return MongoClients.create(mongoClientSettingsBuilder.build(), mongoDriverInformation);
  }

  private static String buildConnectionString(final JsonNode config) {
    final String connectionString = config.get(CONNECTION_STRING_CONFIGURATION_KEY).asText();
    return connectionString +
        "?readPreference=secondary" +
        "&retryWrites=false" +
        "&provider=airbyte" +
        "&tls=true";
  }

}
