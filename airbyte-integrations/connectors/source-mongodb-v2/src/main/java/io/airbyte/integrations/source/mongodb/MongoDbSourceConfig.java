/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.CAPTURE_MODE_LOOKUP_OPTION;
import static io.airbyte.integrations.source.mongodb.MongoConstants.CHECKPOINT_INTERVAL;
import static io.airbyte.integrations.source.mongodb.MongoConstants.CHECKPOINT_INTERVAL_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIG_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DEFAULT_AUTH_SOURCE;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DEFAULT_DISCOVER_SAMPLE_SIZE;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DEFAULT_INITIAL_RECORD_WAITING_TIME_SEC;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DISCOVER_SAMPLE_SIZE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.INITIAL_RECORD_WAITING_TIME_SEC;
import static io.airbyte.integrations.source.mongodb.MongoConstants.INVALID_CDC_CURSOR_POSITION_PROPERTY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.PASSWORD_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.RESYNC_DATA_OPTION;
import static io.airbyte.integrations.source.mongodb.MongoConstants.SCHEMA_ENFORCED_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.UPDATE_CAPTURE_MODE;
import static io.airbyte.integrations.source.mongodb.MongoConstants.USERNAME_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.OptionalInt;

/**
 * Represents the source's configuration, hiding the details of how the underlying JSON
 * configuration is constructed.
 *
 * @param rawConfig The underlying JSON configuration provided by the connector framework.
 */
public record MongoDbSourceConfig(JsonNode rawConfig) {

  public MongoDbSourceConfig {
    if (rawConfig == null) {
      throw new IllegalArgumentException("MongoDbSourceConfig cannot accept a null config.");
    }
    if (!rawConfig.hasNonNull(DATABASE_CONFIG_CONFIGURATION_KEY)) {
      throw new IllegalArgumentException("Database configuration is missing required '" + DATABASE_CONFIG_CONFIGURATION_KEY + "' property.");
    }
  }

  public JsonNode getDatabaseConfig() {
    JsonNode rawDbConfigNode = rawConfig.get(DATABASE_CONFIG_CONFIGURATION_KEY);
    // Add other properties to the raw db config. Unfortunately, due to the setup of the config json,
    // other connection properties need to
    // be added to this config.
    addAdvancedPropertiesToDatabaseConfig(rawDbConfigNode);
    return rawDbConfigNode;
  }

  public String getAuthSource() {
    return getDatabaseConfig().has(AUTH_SOURCE_CONFIGURATION_KEY) ? getDatabaseConfig().get(AUTH_SOURCE_CONFIGURATION_KEY).asText(DEFAULT_AUTH_SOURCE)
        : DEFAULT_AUTH_SOURCE;
  }

  public Integer getCheckpointInterval() {
    return getDatabaseConfig().has(CHECKPOINT_INTERVAL_CONFIGURATION_KEY)
        ? getDatabaseConfig().get(CHECKPOINT_INTERVAL_CONFIGURATION_KEY).asInt(CHECKPOINT_INTERVAL)
        : CHECKPOINT_INTERVAL;
  }

  public String getDatabaseName() {
    return getDatabaseConfig().has(DATABASE_CONFIGURATION_KEY) ? getDatabaseConfig().get(DATABASE_CONFIGURATION_KEY).asText() : null;
  }

  public OptionalInt getQueueSize() {
    return rawConfig.has(MongoConstants.QUEUE_SIZE_CONFIGURATION_KEY)
        ? OptionalInt.of(rawConfig.get(MongoConstants.QUEUE_SIZE_CONFIGURATION_KEY).asInt())
        : OptionalInt.empty();
  }

  public String getPassword() {
    return getDatabaseConfig().has(PASSWORD_CONFIGURATION_KEY) ? getDatabaseConfig().get(PASSWORD_CONFIGURATION_KEY).asText() : null;
  }

  public String getUsername() {
    return getDatabaseConfig().has(USERNAME_CONFIGURATION_KEY) ? getDatabaseConfig().get(USERNAME_CONFIGURATION_KEY).asText() : null;
  }

  public boolean hasAuthCredentials() {
    return getDatabaseConfig().has(USERNAME_CONFIGURATION_KEY) && getDatabaseConfig().has(PASSWORD_CONFIGURATION_KEY);
  }

  public Integer getSampleSize() {
    if (rawConfig.has(DISCOVER_SAMPLE_SIZE_CONFIGURATION_KEY)) {
      return rawConfig.get(DISCOVER_SAMPLE_SIZE_CONFIGURATION_KEY).asInt(DEFAULT_DISCOVER_SAMPLE_SIZE);
    } else {
      return DEFAULT_DISCOVER_SAMPLE_SIZE;
    }
  }

  public boolean getEnforceSchema() {
    return getDatabaseConfig().has(SCHEMA_ENFORCED_CONFIGURATION_KEY) ? getDatabaseConfig().get(SCHEMA_ENFORCED_CONFIGURATION_KEY).asBoolean(true)
        : true;
  }

  public Integer getInitialWaitingTimeSeconds() {
    if (rawConfig.has(INITIAL_RECORD_WAITING_TIME_SEC)) {
      return rawConfig.get(INITIAL_RECORD_WAITING_TIME_SEC).asInt(DEFAULT_INITIAL_RECORD_WAITING_TIME_SEC);
    } else {
      return DEFAULT_INITIAL_RECORD_WAITING_TIME_SEC;
    }
  }

  public boolean shouldFailSyncOnInvalidCursor() {
    if (rawConfig.has(INVALID_CDC_CURSOR_POSITION_PROPERTY)
        && rawConfig.get(INVALID_CDC_CURSOR_POSITION_PROPERTY).asText().equals(RESYNC_DATA_OPTION)) {
      return false;
    } else {
      return true;
    }
  }

  public String getUpdateCaptureMode() {
    if (rawConfig.has(UPDATE_CAPTURE_MODE)) {
      return rawConfig.get(UPDATE_CAPTURE_MODE).asText();
    } else {
      return CAPTURE_MODE_LOOKUP_OPTION;
    }
  }

  private void addAdvancedPropertiesToDatabaseConfig(JsonNode dbConfig) {
    ((ObjectNode) dbConfig).put(UPDATE_CAPTURE_MODE, getUpdateCaptureMode());
  }

}
