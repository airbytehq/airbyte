/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.integrations.source.mongodb.MongoConstants.CAPTURE_MODE_POST_IMAGE_OPTION;
import static io.airbyte.integrations.source.mongodb.MongoConstants.UPDATE_CAPTURE_MODE;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.Configuration.AUTH_SOURCE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.Configuration.CREDENTIALS_PLACEHOLDER;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.Configuration.PASSWORD_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.Configuration.USERNAME_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.List;
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

  static final String MONGODB_POST_IMAGE_KEY = "capture.mode.full.update.type";
  static final String MONGODB_POST_IMAGE_VALUE = "post_image";
  static final String CAPTURE_TARGET_KEY = "capture.target";
  static final String DOUBLE_QUOTES_PATTERN = "\"";
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
                                          final ConfiguredAirbyteCatalog catalog) {
    super(properties, config, catalog);
  }

  @Override
  protected Properties getConnectionConfiguration(final JsonNode config) {
    final Properties properties = new Properties();

    properties.setProperty(MONGODB_CONNECTION_STRING_KEY, buildConnectionString(config));
    properties.setProperty(MONGODB_CONNECTION_MODE_KEY, MONGODB_CONNECTION_MODE_VALUE);

    if (config.has(USERNAME_CONFIGURATION_KEY)) {
      properties.setProperty(MONGODB_USER_KEY, config.get(USERNAME_CONFIGURATION_KEY).asText());
    }
    if (config.has(PASSWORD_CONFIGURATION_KEY)) {
      properties.setProperty(MONGODB_PASSWORD_KEY, config.get(PASSWORD_CONFIGURATION_KEY).asText());
    }
    if (config.has(AUTH_SOURCE_CONFIGURATION_KEY)) {
      properties.setProperty(MONGODB_AUTHSOURCE_KEY, config.get(AUTH_SOURCE_CONFIGURATION_KEY).asText());
    }
    properties.setProperty(MONGODB_SSL_ENABLED_KEY, MONGODB_SSL_ENABLED_VALUE);
    if (config.has(UPDATE_CAPTURE_MODE) && config.get(UPDATE_CAPTURE_MODE).asText().equals(CAPTURE_MODE_POST_IMAGE_OPTION)) {
      properties.setProperty(MONGODB_POST_IMAGE_KEY, MONGODB_POST_IMAGE_VALUE);
    }
    return properties;
  }

  @Override
  protected String getName(final JsonNode config) {
    return normalizeName(config.get(DATABASE_CONFIGURATION_KEY).asText());
  }

  @Override
  protected Properties getIncludeConfiguration(final ConfiguredAirbyteCatalog catalog, final JsonNode config) {
    final Properties properties = new Properties();

    // Database/collection selection
    properties.setProperty(COLLECTION_INCLUDE_LIST_KEY, createCollectionIncludeString(catalog.getStreams()));
    properties.setProperty(DATABASE_INCLUDE_LIST_KEY, config.get(DATABASE_CONFIGURATION_KEY).asText());
    properties.setProperty(CAPTURE_TARGET_KEY, config.get(DATABASE_CONFIGURATION_KEY).asText());

    return properties;
  }

  protected String createCollectionIncludeString(final List<ConfiguredAirbyteStream> streams) {
    return streams.stream()
        .map(s -> s.getStream().getNamespace() + "\\." + s.getStream().getName())
        .collect(Collectors.joining(","));
  }

  /**
   * Ensure that the name property is formatted correctly for use by Debezium.
   *
   * @param name The name to be associated with the Debezium connector.
   * @return The normalized name.
   */
  public static String normalizeName(final String name) {
    return name != null ? name.replaceAll("_", "-") : null;
  }

  /**
   * Builds the MongoDB connection string from the provided configuration. This method handles
   * removing any values accidentally copied and pasted from the MongoDB Atlas UI.
   *
   * @param config The connector configuration.
   * @return The connection string.
   */
  public static String buildConnectionString(final JsonNode config) {
    final String connectionString = config.get(CONNECTION_STRING_CONFIGURATION_KEY)
        .asText()
        .trim()
        .replaceAll(DOUBLE_QUOTES_PATTERN, "")
        .replaceAll(CREDENTIALS_PLACEHOLDER, "");
    final StringBuilder builder = new StringBuilder();
    builder.append(connectionString);
    return builder.toString();
  }

}
