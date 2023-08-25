/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mongodb;

import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.AUTH_SOURCE_CONFIGURATION_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.PASSWORD_CONFIGURATION_KEY;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.Configuration.USER_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.List;
import java.util.Optional;
import java.util.Properties;
import java.util.stream.Collectors;

/**
 * Custom {@link DebeziumPropertiesManager} specific for the configuration of the Debezium MongoDB
 * connector.
 * <p />
 * This implementation provides the specific connection properties required for the Debezium MongoDB
 * connector. These properties differ from the general relational database connection properties
 * used by the other Debezium connectors.
 */
public class MongoDbDebeziumPropertiesManager extends DebeziumPropertiesManager {

  static final String COLLECTION_INCLUDE_LIST_KEY = "collection.include.list";
  static final String DATABASE_INCLUDE_LIST_KEY = "database.include.list";
  static final String MONGODB_AUTHSOURCE_KEY = "mongodb.authsource";
  static final String MONGODB_CONNECTION_MODE_KEY = "mongodb.connection.mode";
  static final String MONGODB_CONNECTION_MODE_VALUE = "replica_set";
  static final String MONGODB_CONNECTION_STRING_KEY = "mongodb.connection.string";
  static final String MONGODB_PASSWORD_KEY = "mongodb.password";
  static final String MONGODB_SSL_ENABLED_KEY = "mongodb.ssl.enabled";
  static final String MONGODB_SSL_ENABLED_VALUE = Boolean.TRUE.toString();
  static final String MONGODB_USER_KEY = "mongodb.user";

  public MongoDbDebeziumPropertiesManager(final Properties properties,
                                          final JsonNode config,
                                          final ConfiguredAirbyteCatalog catalog,
                                          final AirbyteFileOffsetBackingStore offsetManager,
                                          final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager) {
    super(properties, config, catalog, offsetManager, schemaHistoryManager);
  }

  @Override
  protected Properties getConnectionConfiguration(final JsonNode config) {
    final Properties properties = new Properties();

    properties.setProperty(MONGODB_CONNECTION_STRING_KEY, config.get(CONNECTION_STRING_CONFIGURATION_KEY).asText());
    properties.setProperty(MONGODB_CONNECTION_MODE_KEY, MONGODB_CONNECTION_MODE_VALUE);

    if (config.has(USER_CONFIGURATION_KEY)) {
      properties.setProperty(MONGODB_USER_KEY, config.get(USER_CONFIGURATION_KEY).asText());
    }
    if (config.has(PASSWORD_CONFIGURATION_KEY)) {
      properties.setProperty(MONGODB_PASSWORD_KEY, config.get(PASSWORD_CONFIGURATION_KEY).asText());
    }
    if (config.has(AUTH_SOURCE_CONFIGURATION_KEY)) {
      properties.setProperty(MONGODB_AUTHSOURCE_KEY, config.get(AUTH_SOURCE_CONFIGURATION_KEY).asText());
    }
    properties.setProperty(MONGODB_SSL_ENABLED_KEY, MONGODB_SSL_ENABLED_VALUE);
    return properties;
  }

  @Override
  protected String getName(final JsonNode config) {
    return config.get(DATABASE_CONFIGURATION_KEY).asText().replaceAll("_", "-");
  }

  @Override
  protected Properties getIncludeConfiguration(final ConfiguredAirbyteCatalog catalog, final JsonNode config) {
    final Properties properties = new Properties();

    // Database/collection selection
    properties.setProperty(COLLECTION_INCLUDE_LIST_KEY, createCollectionIncludeString(catalog.getStreams()));
    properties.setProperty(DATABASE_INCLUDE_LIST_KEY, config.get(DATABASE_CONFIGURATION_KEY).asText());

    return properties;
  }

  protected String createCollectionIncludeString(final List<ConfiguredAirbyteStream> streams) {
    return streams.stream()
        .map(s -> s.getStream().getNamespace() + "\\." + s.getStream().getName())
        .collect(Collectors.joining(","));
  }

}
