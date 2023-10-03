/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals.mongodb;

import static io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager.NAME_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager.TOPIC_PREFIX_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.AUTH_SOURCE_CONFIGURATION_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.CREDENTIALS_PLACEHOLDER;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.PASSWORD_CONFIGURATION_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.USERNAME_CONFIGURATION_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.COLLECTION_INCLUDE_LIST_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.DATABASE_INCLUDE_LIST_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_AUTHSOURCE_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_CONNECTION_MODE_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_CONNECTION_MODE_VALUE;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_CONNECTION_STRING_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_PASSWORD_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_SSL_ENABLED_KEY;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_SSL_ENABLED_VALUE;
import static io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager.MONGODB_USER_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.commons.json.Jsons;
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
  public static final String EXPECTED_CONNECTION_STRING = "mongodb://localhost:27017/?retryWrites=false&provider=airbyte&tls=true";

  @Test
  void testDebeziumProperties() {
    final List<ConfiguredAirbyteStream> streams = createStreams(4);
    final AirbyteFileOffsetBackingStore offsetManager = mock(AirbyteFileOffsetBackingStore.class);
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final JsonNode config = createConfiguration(Optional.of("username"), Optional.of("password"), Optional.of("admin"));

    when(offsetManager.getOffsetFilePath()).thenReturn(PATH);
    when(catalog.getStreams()).thenReturn(streams);

    final Properties cdcProperties = new Properties();
    cdcProperties.put("test", "value");

    final MongoDbDebeziumPropertiesManager debeziumPropertiesManager = new MongoDbDebeziumPropertiesManager(
        cdcProperties,
        config,
        catalog,
        offsetManager);

    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties();
    assertEquals(22 + cdcProperties.size(), debeziumProperties.size());
    assertEquals(MongoDbDebeziumPropertiesManager.normalizeName(DATABASE_NAME), debeziumProperties.get(NAME_KEY));
    assertEquals(MongoDbDebeziumPropertiesManager.normalizeName(DATABASE_NAME), debeziumProperties.get(TOPIC_PREFIX_KEY));
    assertEquals(EXPECTED_CONNECTION_STRING, debeziumProperties.get(MONGODB_CONNECTION_STRING_KEY));
    assertEquals(MONGODB_CONNECTION_MODE_VALUE, debeziumProperties.get(MONGODB_CONNECTION_MODE_KEY));
    assertEquals(config.get(USERNAME_CONFIGURATION_KEY).asText(), debeziumProperties.get(MONGODB_USER_KEY));
    assertEquals(config.get(PASSWORD_CONFIGURATION_KEY).asText(), debeziumProperties.get(MONGODB_PASSWORD_KEY));
    assertEquals(config.get(AUTH_SOURCE_CONFIGURATION_KEY).asText(), debeziumProperties.get(MONGODB_AUTHSOURCE_KEY));
    assertEquals(MONGODB_SSL_ENABLED_VALUE, debeziumProperties.get(MONGODB_SSL_ENABLED_KEY));
    assertEquals(debeziumPropertiesManager.createCollectionIncludeString(streams), debeziumProperties.get(COLLECTION_INCLUDE_LIST_KEY));
    assertEquals(DATABASE_NAME, debeziumProperties.get(DATABASE_INCLUDE_LIST_KEY));
  }

  @Test
  void testDebeziumPropertiesConnectionStringCredentialsPlaceholder() {
    final List<ConfiguredAirbyteStream> streams = createStreams(4);
    final AirbyteFileOffsetBackingStore offsetManager = mock(AirbyteFileOffsetBackingStore.class);
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final JsonNode config = createConfiguration(Optional.of("username"), Optional.of("password"), Optional.of("admin"));
    ((ObjectNode) config).put(CONNECTION_STRING_CONFIGURATION_KEY, config.get(CONNECTION_STRING_CONFIGURATION_KEY).asText()
        .replaceAll("mongodb://", "mongodb://" + CREDENTIALS_PLACEHOLDER));

    when(offsetManager.getOffsetFilePath()).thenReturn(PATH);
    when(catalog.getStreams()).thenReturn(streams);

    final Properties cdcProperties = new Properties();
    cdcProperties.put("test", "value");

    final MongoDbDebeziumPropertiesManager debeziumPropertiesManager = new MongoDbDebeziumPropertiesManager(
        cdcProperties,
        config,
        catalog,
        offsetManager);

    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties();
    assertEquals(22 + cdcProperties.size(), debeziumProperties.size());
    assertEquals(MongoDbDebeziumPropertiesManager.normalizeName(DATABASE_NAME), debeziumProperties.get(NAME_KEY));
    assertEquals(MongoDbDebeziumPropertiesManager.normalizeName(DATABASE_NAME), debeziumProperties.get(TOPIC_PREFIX_KEY));
    assertEquals(EXPECTED_CONNECTION_STRING, debeziumProperties.get(MONGODB_CONNECTION_STRING_KEY));
    assertEquals(MONGODB_CONNECTION_MODE_VALUE, debeziumProperties.get(MONGODB_CONNECTION_MODE_KEY));
    assertEquals(config.get(USERNAME_CONFIGURATION_KEY).asText(), debeziumProperties.get(MONGODB_USER_KEY));
    assertEquals(config.get(PASSWORD_CONFIGURATION_KEY).asText(), debeziumProperties.get(MONGODB_PASSWORD_KEY));
    assertEquals(config.get(AUTH_SOURCE_CONFIGURATION_KEY).asText(), debeziumProperties.get(MONGODB_AUTHSOURCE_KEY));
    assertEquals(MONGODB_SSL_ENABLED_VALUE, debeziumProperties.get(MONGODB_SSL_ENABLED_KEY));
    assertEquals(debeziumPropertiesManager.createCollectionIncludeString(streams), debeziumProperties.get(COLLECTION_INCLUDE_LIST_KEY));
    assertEquals(DATABASE_NAME, debeziumProperties.get(DATABASE_INCLUDE_LIST_KEY));
  }

  @Test
  void testDebeziumPropertiesQuotedConnectionString() {
    final List<ConfiguredAirbyteStream> streams = createStreams(4);
    final AirbyteFileOffsetBackingStore offsetManager = mock(AirbyteFileOffsetBackingStore.class);
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final JsonNode config = createConfiguration(Optional.of("username"), Optional.of("password"), Optional.of("admin"));
    ((ObjectNode) config).put(CONNECTION_STRING_CONFIGURATION_KEY, "\"" + config.get(CONNECTION_STRING_CONFIGURATION_KEY) + "\"");

    when(offsetManager.getOffsetFilePath()).thenReturn(PATH);
    when(catalog.getStreams()).thenReturn(streams);

    final Properties cdcProperties = new Properties();
    cdcProperties.put("test", "value");

    final MongoDbDebeziumPropertiesManager debeziumPropertiesManager = new MongoDbDebeziumPropertiesManager(
        cdcProperties,
        config,
        catalog,
        offsetManager);

    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties();
    assertEquals(22 + cdcProperties.size(), debeziumProperties.size());
    assertEquals(MongoDbDebeziumPropertiesManager.normalizeName(DATABASE_NAME), debeziumProperties.get(NAME_KEY));
    assertEquals(MongoDbDebeziumPropertiesManager.normalizeName(DATABASE_NAME), debeziumProperties.get(TOPIC_PREFIX_KEY));
    assertEquals(EXPECTED_CONNECTION_STRING, debeziumProperties.get(MONGODB_CONNECTION_STRING_KEY));
    assertEquals(MONGODB_CONNECTION_MODE_VALUE, debeziumProperties.get(MONGODB_CONNECTION_MODE_KEY));
    assertEquals(config.get(USERNAME_CONFIGURATION_KEY).asText(), debeziumProperties.get(MONGODB_USER_KEY));
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
    when(catalog.getStreams()).thenReturn(streams);

    final Properties cdcProperties = new Properties();
    cdcProperties.put("test", "value");

    final MongoDbDebeziumPropertiesManager debeziumPropertiesManager = new MongoDbDebeziumPropertiesManager(
        cdcProperties,
        config,
        catalog,
        offsetManager);

    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties();
    assertEquals(19 + cdcProperties.size(), debeziumProperties.size());
    assertEquals(MongoDbDebeziumPropertiesManager.normalizeName(DATABASE_NAME), debeziumProperties.get(NAME_KEY));
    assertEquals(MongoDbDebeziumPropertiesManager.normalizeName(DATABASE_NAME), debeziumProperties.get(TOPIC_PREFIX_KEY));
    assertEquals(EXPECTED_CONNECTION_STRING, debeziumProperties.get(MONGODB_CONNECTION_STRING_KEY));
    assertEquals(MONGODB_CONNECTION_MODE_VALUE, debeziumProperties.get(MONGODB_CONNECTION_MODE_KEY));
    assertFalse(debeziumProperties.containsKey(MONGODB_USER_KEY));
    assertFalse(debeziumProperties.containsKey(MONGODB_PASSWORD_KEY));
    assertFalse(debeziumProperties.containsKey(MONGODB_AUTHSOURCE_KEY));
    assertEquals(MONGODB_SSL_ENABLED_VALUE, debeziumProperties.get(MONGODB_SSL_ENABLED_KEY));
    assertEquals(debeziumPropertiesManager.createCollectionIncludeString(streams), debeziumProperties.get(COLLECTION_INCLUDE_LIST_KEY));
    assertEquals(DATABASE_NAME, debeziumProperties.get(DATABASE_INCLUDE_LIST_KEY));
  }

  @Test
  void testNormalizeName() {
    final String nameWithUnderscore = "name_with_underscore";
    final String nameWithoutUnderscore = "nameWithout-Underscore";
    final String blankName = "";
    final String nullName = null;

    assertEquals("name-with-underscore", MongoDbDebeziumPropertiesManager.normalizeName(nameWithUnderscore));
    assertEquals(nameWithoutUnderscore, MongoDbDebeziumPropertiesManager.normalizeName(nameWithoutUnderscore));
    assertEquals(blankName, MongoDbDebeziumPropertiesManager.normalizeName(blankName));
    assertNull(MongoDbDebeziumPropertiesManager.normalizeName(nullName));

  }

  @Test
  void testCreateConnectionString() {
    final JsonNode config = createConfiguration(Optional.of("username"), Optional.of("password"), Optional.of("admin"));
    final String connectionString = MongoDbDebeziumPropertiesManager.buildConnectionString(config, false);
    assertNotNull(connectionString);
    assertEquals(EXPECTED_CONNECTION_STRING, connectionString);
  }

  @Test
  void testCreateConnectionStringQuotedString() {
    final JsonNode config = createConfiguration(Optional.of("username"), Optional.of("password"), Optional.of("admin"));
    final String connectionString = MongoDbDebeziumPropertiesManager.buildConnectionString(config, false);
    ((ObjectNode) config).put(CONNECTION_STRING_CONFIGURATION_KEY, "\"" + config.get(CONNECTION_STRING_CONFIGURATION_KEY) + "\"");
    assertNotNull(connectionString);
    assertEquals(EXPECTED_CONNECTION_STRING, connectionString);
  }

  @Test
  void testCreateConnectionStringUseSecondary() {
    final JsonNode config = createConfiguration(Optional.of("username"), Optional.of("password"), Optional.of("admin"));
    final String connectionString = MongoDbDebeziumPropertiesManager.buildConnectionString(config, true);
    assertNotNull(connectionString);
    assertEquals("mongodb://localhost:27017/?retryWrites=false&provider=airbyte&tls=true&readPreference=secondary", connectionString);
  }

  @Test
  void testCreateConnectionStringPlaceholderCredentials() {
    final JsonNode config = createConfiguration(Optional.of("username"), Optional.of("password"), Optional.of("admin"));
    ((ObjectNode) config).put(CONNECTION_STRING_CONFIGURATION_KEY, config.get(CONNECTION_STRING_CONFIGURATION_KEY).asText()
        .replaceAll("mongodb://", "mongodb://" + CREDENTIALS_PLACEHOLDER));
    final String connectionString = MongoDbDebeziumPropertiesManager.buildConnectionString(config, false);
    assertNotNull(connectionString);
    assertEquals(EXPECTED_CONNECTION_STRING, connectionString);
  }

  private JsonNode createConfiguration(final Optional<String> username, final Optional<String> password, final Optional<String> authMode) {
    final Map<String, Object> baseConfig = Map.of(
        DATABASE_CONFIGURATION_KEY, DATABASE_NAME,
        CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://localhost:27017/");

    final Map<String, Object> config = new HashMap<>(baseConfig);
    authMode.ifPresent(a -> config.put(AUTH_SOURCE_CONFIGURATION_KEY, a));
    username.ifPresent(u -> config.put(USERNAME_CONFIGURATION_KEY, u));
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
