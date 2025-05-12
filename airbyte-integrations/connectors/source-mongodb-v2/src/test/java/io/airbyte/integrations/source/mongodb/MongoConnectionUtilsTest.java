/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.MongoConstants.CREDENTIALS_PLACEHOLDER;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIG_CONFIGURATION_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

import com.mongodb.ServerAddress;
import com.mongodb.client.MongoClient;
import com.mongodb.client.internal.MongoClientImpl;
import io.airbyte.commons.json.Jsons;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class MongoConnectionUtilsTest {

  @Test
  void testCreateMongoClient() {
    final String authSource = "admin";
    final String host = "host";
    final int port = 1234;
    final String username = "user";
    final String password = "password";
    final MongoDbSourceConfig config = new MongoDbSourceConfig(Jsons.jsonNode(
        Map.of(DATABASE_CONFIG_CONFIGURATION_KEY,
            Map.of(
                MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://" + host + ":" + port + "/",
                MongoConstants.USERNAME_CONFIGURATION_KEY, username,
                MongoConstants.PASSWORD_CONFIGURATION_KEY, password,
                MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY, authSource))));

    final MongoClient mongoClient = MongoConnectionUtils.createMongoClient(config);

    assertNotNull(mongoClient);
    assertEquals(List.of(new ServerAddress(host, port)), ((MongoClientImpl) mongoClient).getSettings().getClusterSettings().getHosts());
    assertEquals(List.of("sync", MongoConstants.DRIVER_NAME), ((MongoClientImpl) mongoClient).getMongoDriverInformation().getDriverNames());
    assertEquals(username, ((MongoClientImpl) mongoClient).getSettings().getCredential().getUserName());
    assertEquals(password, new String(((MongoClientImpl) mongoClient).getSettings().getCredential().getPassword()));
    assertEquals(authSource, ((MongoClientImpl) mongoClient).getSettings().getCredential().getSource());
    // read prefernce defaults to primary
    // https://mongodb.github.io/mongo-java-driver/3.9/javadoc/com/mongodb/MongoClientSettings.html#getReadPreference--
    assertEquals(ReadPreference.primary(), ((MongoClientImpl) mongoClient).getSettings().getReadPreference());
  }

  @Test
  void testCreateMongoClientWithReadPreference() {
    final String authSource = "admin";
    final String host = "host";
    final int port = 1234;
    final String username = "user";
    final String password = "password";
    final String readPreference = "readPreference=secondary";
    final MongoDbSourceConfig config = new MongoDbSourceConfig(Jsons.jsonNode(
        Map.of(DATABASE_CONFIG_CONFIGURATION_KEY,
            Map.of(
                MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://" + host + ":" + port + "/" + readPreference,
                MongoConstants.USERNAME_CONFIGURATION_KEY, username,
                MongoConstants.PASSWORD_CONFIGURATION_KEY, password,
                MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY, authSource))));

    final MongoClient mongoClient = MongoConnectionUtils.createMongoClient(config);

    assertNotNull(mongoClient);
    assertEquals(List.of(new ServerAddress(host, port)), ((MongoClientImpl) mongoClient).getSettings().getClusterSettings().getHosts());
    assertEquals(List.of("sync", MongoConstants.DRIVER_NAME), ((MongoClientImpl) mongoClient).getMongoDriverInformation().getDriverNames());
    assertEquals(username, ((MongoClientImpl) mongoClient).getSettings().getCredential().getUserName());
    assertEquals(password, new String(((MongoClientImpl) mongoClient).getSettings().getCredential().getPassword()));
    assertEquals(authSource, ((MongoClientImpl) mongoClient).getSettings().getCredential().getSource());
    assertEquals(ReadPreference.secondary(), ((MongoClientImpl) mongoClient).getSettings().getReadPreference());
  }

  @Test
  void testCreateMongoClientWithQuotesInConnectionString() {
    final String authSource = "admin";
    final String host = "host";
    final int port = 1234;
    final String username = "user";
    final String password = "password";
    final MongoDbSourceConfig config = new MongoDbSourceConfig(Jsons.jsonNode(
        Map.of(DATABASE_CONFIG_CONFIGURATION_KEY,
            Map.of(
                MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY, "\"mongodb://" + host + ":" + port + "/\"",
                MongoConstants.USERNAME_CONFIGURATION_KEY, username,
                MongoConstants.PASSWORD_CONFIGURATION_KEY, password,
                MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY, authSource))));

    final MongoClient mongoClient = MongoConnectionUtils.createMongoClient(config);

    assertNotNull(mongoClient);
    assertEquals(List.of(new ServerAddress(host, port)), ((MongoClientImpl) mongoClient).getSettings().getClusterSettings().getHosts());
    assertEquals(List.of("sync", MongoConstants.DRIVER_NAME), ((MongoClientImpl) mongoClient).getMongoDriverInformation().getDriverNames());
    assertEquals(username, ((MongoClientImpl) mongoClient).getSettings().getCredential().getUserName());
    assertEquals(password, new String(((MongoClientImpl) mongoClient).getSettings().getCredential().getPassword()));
    assertEquals(authSource, ((MongoClientImpl) mongoClient).getSettings().getCredential().getSource());
  }

  @Test
  void testCreateMongoClientWithoutCredentials() {
    final String host = "host";
    final int port = 1234;
    final MongoDbSourceConfig config = new MongoDbSourceConfig(Jsons.jsonNode(
        Map.of(DATABASE_CONFIG_CONFIGURATION_KEY,
            Map.of(MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://" + host + ":" + port + "/"))));

    final MongoClient mongoClient = MongoConnectionUtils.createMongoClient(config);

    assertNotNull(mongoClient);
    assertEquals(List.of(new ServerAddress(host, port)), ((MongoClientImpl) mongoClient).getSettings().getClusterSettings().getHosts());
    assertEquals(List.of("sync", MongoConstants.DRIVER_NAME), ((MongoClientImpl) mongoClient).getMongoDriverInformation().getDriverNames());
    assertNull(((MongoClientImpl) mongoClient).getSettings().getCredential());
  }

  @Test
  void testCreateMongoClientWithCredentialPlaceholderInConnectionString() {
    final String authSource = "admin";
    final String host = "host";
    final int port = 1234;
    final String username = "user";
    final String password = "password";
    final MongoDbSourceConfig config = new MongoDbSourceConfig(Jsons.jsonNode(
        Map.of(DATABASE_CONFIG_CONFIGURATION_KEY,
            Map.of(
                MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://" + CREDENTIALS_PLACEHOLDER + host + ":" + port + "/",
                MongoConstants.USERNAME_CONFIGURATION_KEY, username,
                MongoConstants.PASSWORD_CONFIGURATION_KEY, password,
                MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY, authSource))));

    final MongoClient mongoClient = MongoConnectionUtils.createMongoClient(config);

    assertNotNull(mongoClient);
    assertEquals(List.of(new ServerAddress(host, port)), ((MongoClientImpl) mongoClient).getSettings().getClusterSettings().getHosts());
    assertEquals(List.of("sync", MongoConstants.DRIVER_NAME), ((MongoClientImpl) mongoClient).getMongoDriverInformation().getDriverNames());
    assertEquals(username, ((MongoClientImpl) mongoClient).getSettings().getCredential().getUserName());
    assertEquals(password, new String(((MongoClientImpl) mongoClient).getSettings().getCredential().getPassword()));
    assertEquals(authSource, ((MongoClientImpl) mongoClient).getSettings().getCredential().getSource());
  }

}
