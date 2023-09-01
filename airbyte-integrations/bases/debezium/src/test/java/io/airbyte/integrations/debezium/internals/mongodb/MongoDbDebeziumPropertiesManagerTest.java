/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mongodb;

import static io.airbyte.integrations.debezium.internals.DebeziumPropertiesManager.NAME_KEY;
import static io.airbyte.integrations.debezium.internals.DebeziumPropertiesManager.TOPIC_PREFIX_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.AUTH_SOURCE_CONFIGURATION_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.PASSWORD_CONFIGURATION_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.REPLICA_SET_CONFIGURATION_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.USER_CONFIGURATION_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.COLLECTION_INCLUDE_LIST_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.DATABASE_INCLUDE_LIST_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_AUTHSOURCE_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_CONNECTION_MODE_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_CONNECTION_MODE_VALUE;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_CONNECTION_STRING_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_PASSWORD_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_SSL_ENABLED_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_SSL_ENABLED_VALUE;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_USER_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;
import org.junit.jupiter.api.Test;

class MongoDbDebeziumPropertiesManagerTest {

  private static final String DATABASE_NAME = "test_database";
  private static final Path PATH = Path.of(".");

  @Test
  void testDebeziumProperties() {
    final List<ConfiguredAirbyteStream> streams = createStreams(4);
    final AirbyteFileOffsetBackingStore offsetManager = mock(AirbyteFileOffsetBackingStore.class);
    final AirbyteSchemaHistoryStorage schemaHistoryManager = mock(AirbyteSchemaHistoryStorage.class);
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final JsonNode config = createConfiguration(Optional.of("username"), Optional.of("password"), Optional.of("admin"));

    when(offsetManager.getOffsetFilePath()).thenReturn(PATH);
    when(schemaHistoryManager.getPath()).thenReturn(PATH);
    when(catalog.getStreams()).thenReturn(streams);

    final Properties cdcProperties = new Properties();
    cdcProperties.put("test", "value");

    final MongoDbDebeziumPropertiesManager debeziumPropertiesManager = new MongoDbDebeziumPropertiesManager(
        cdcProperties,
        config,
        catalog,
        offsetManager,
        Optional.of(schemaHistoryManager));

    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties();
    assertEquals(24 + cdcProperties.size(), debeziumProperties.size());
    assertEquals(DATABASE_NAME.replaceAll("_", "-"), debeziumProperties.get(NAME_KEY));
    assertEquals(DATABASE_NAME.replaceAll("_", "-"), debeziumProperties.get(TOPIC_PREFIX_KEY));
    assertEquals(config.get(CONNECTION_STRING_CONFIGURATION_KEY).asText(), debeziumProperties.get(MONGODB_CONNECTION_STRING_KEY));
    assertEquals(MONGODB_CONNECTION_MODE_VALUE, debeziumProperties.get(MONGODB_CONNECTION_MODE_KEY));
    assertEquals(config.get(USER_CONFIGURATION_KEY).asText(), debeziumProperties.get(MONGODB_USER_KEY));
    assertEquals(config.get(PASSWORD_CONFIGURATION_KEY).asText(), debeziumProperties.get(MONGODB_PASSWORD_KEY));
    assertEquals(config.get(AUTH_SOURCE_CONFIGURATION_KEY).asText(), debeziumProperties.get(MONGODB_AUTHSOURCE_KEY));
    assertEquals(MONGODB_SSL_ENABLED_VALUE, debeziumProperties.get(MONGODB_SSL_ENABLED_KEY));
    assertEquals(debeziumPropertiesManager.createCollectionIncludeString(streams), debeziumProperties.get(COLLECTION_INCLUDE_LIST_KEY));
    assertEquals(DATABASE_NAME, debeziumProperties.get(DATABASE_INCLUDE_LIST_KEY));
  }

  @Test
  void testDebeziumPropertiesNoCredentials() {
    final List<ConfiguredAirbyteStream> streams = createStreams(4);
    final AirbyteFileOffsetBackingStore offsetManager = mock(AirbyteFileOffsetBackingStore.class);
    final AirbyteSchemaHistoryStorage schemaHistoryManager = mock(AirbyteSchemaHistoryStorage.class);
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final JsonNode config = createConfiguration(Optional.empty(), Optional.empty(), Optional.empty());

    when(offsetManager.getOffsetFilePath()).thenReturn(PATH);
    when(schemaHistoryManager.getPath()).thenReturn(PATH);
    when(catalog.getStreams()).thenReturn(streams);

    final Properties cdcProperties = new Properties();
    cdcProperties.put("test", "value");

    final MongoDbDebeziumPropertiesManager debeziumPropertiesManager = new MongoDbDebeziumPropertiesManager(
        cdcProperties,
        config,
        catalog,
        offsetManager,
        Optional.of(schemaHistoryManager));

    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties();
    assertEquals(21 + cdcProperties.size(), debeziumProperties.size());
    assertEquals(DATABASE_NAME.replaceAll("_", "-"), debeziumProperties.get(NAME_KEY));
    assertEquals(DATABASE_NAME.replaceAll("_", "-"), debeziumProperties.get(TOPIC_PREFIX_KEY));
    assertEquals(config.get(CONNECTION_STRING_CONFIGURATION_KEY).asText(), debeziumProperties.get(MONGODB_CONNECTION_STRING_KEY));
    assertEquals(MONGODB_CONNECTION_MODE_VALUE, debeziumProperties.get(MONGODB_CONNECTION_MODE_KEY));
    assertFalse(debeziumProperties.containsKey(MONGODB_USER_KEY));
    assertFalse(debeziumProperties.containsKey(MONGODB_PASSWORD_KEY));
    assertFalse(debeziumProperties.containsKey(MONGODB_AUTHSOURCE_KEY));
    assertEquals(MONGODB_SSL_ENABLED_VALUE, debeziumProperties.get(MONGODB_SSL_ENABLED_KEY));
    assertEquals(debeziumPropertiesManager.createCollectionIncludeString(streams), debeziumProperties.get(COLLECTION_INCLUDE_LIST_KEY));
    assertEquals(DATABASE_NAME, debeziumProperties.get(DATABASE_INCLUDE_LIST_KEY));
  }

  private JsonNode createConfiguration(final Optional<String> username, final Optional<String> password, final Optional<String> authMode) {
    final Map<String, Object> config = new HashMap<>();
    final Map<String, Object> baseConfig = Map.of(
        DATABASE_CONFIGURATION_KEY, DATABASE_NAME,
        CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://localhost:27017/",
        REPLICA_SET_CONFIGURATION_KEY, "replica-set");

    config.putAll(baseConfig);
    authMode.ifPresent(a -> config.put(AUTH_SOURCE_CONFIGURATION_KEY, a));
    username.ifPresent(u -> config.put(USER_CONFIGURATION_KEY, u));
    password.ifPresent(p -> config.put(PASSWORD_CONFIGURATION_KEY, p));
    return Jsons.deserialize(Jsons.serialize(config));
  }

  private List<ConfiguredAirbyteStream> createStreams(final int numberOfStreams) {
    final List<ConfiguredAirbyteStream> streams = new ArrayList<>();
    for (int i = 0; i < numberOfStreams; i++) {
      final AirbyteStream stream = new AirbyteStream().withNamespace(DATABASE_NAME).withName("collection" + i);
      streams.add(new ConfiguredAirbyteStream().withStream(stream));
    }
    return streams;
  }

}
