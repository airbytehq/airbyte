/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.MongoConstants.DRIVER_NAME;

import com.mongodb.ConnectionString;
import com.mongodb.MongoClientSettings;
import com.mongodb.MongoCredential;
import com.mongodb.MongoDriverInformation;
import com.mongodb.ReadPreference;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumPropertiesManager;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

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
  public static MongoClient createMongoClient(final MongoDbSourceConfig config) {
    final ConnectionString mongoConnectionString = new ConnectionString(buildConnectionString(config));

    final MongoDriverInformation mongoDriverInformation = MongoDriverInformation.builder()
        .driverName(DRIVER_NAME)
        .build();

    final MongoClientSettings.Builder mongoClientSettingsBuilder = MongoClientSettings.builder()
        .applyConnectionString(mongoConnectionString)
        .readPreference(ReadPreference.secondaryPreferred());

    if (config.hasAuthCredentials()) {
      final String authSource = config.getAuthSource();
      final String user = URLEncoder.encode(config.getUsername(), StandardCharsets.UTF_8);
      final String password = config.getPassword();
      mongoClientSettingsBuilder.credential(MongoCredential.createCredential(user, authSource, password.toCharArray()));
    }

    return MongoClients.create(mongoClientSettingsBuilder.build(), mongoDriverInformation);
  }

  private static String buildConnectionString(final MongoDbSourceConfig config) {
    return MongoDbDebeziumPropertiesManager.buildConnectionString(config.getDatabaseConfig());
  }

}
