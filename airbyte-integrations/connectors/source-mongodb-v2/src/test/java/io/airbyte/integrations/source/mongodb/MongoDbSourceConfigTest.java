/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.CHECKPOINT_INTERVAL;
import static io.airbyte.integrations.source.mongodb.MongoConstants.CHECKPOINT_INTERVAL_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIG_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DEFAULT_AUTH_SOURCE;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DEFAULT_DISCOVER_SAMPLE_SIZE;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DISCOVER_SAMPLE_SIZE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.PASSWORD_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.QUEUE_SIZE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.SCHEMA_ENFORCED_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.USERNAME_CONFIGURATION_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.util.Map;
import java.util.OptionalInt;
import org.junit.jupiter.api.Test;

class MongoDbSourceConfigTest {

  @Test
  void testCreatingMongoDbSourceConfig() {
    final String authSource = "auth";
    final Integer checkpointInterval = 1;
    final String database = "database";
    final Integer queueSize = 1;
    final String password = "password";
    final Integer sampleSize = 5000;
    final String username = "username";
    final boolean isSchemaEnforced = false;
    final JsonNode rawConfig = Jsons.jsonNode(
        Map.of(
            DISCOVER_SAMPLE_SIZE_CONFIGURATION_KEY, sampleSize,
            QUEUE_SIZE_CONFIGURATION_KEY, queueSize,
            DATABASE_CONFIG_CONFIGURATION_KEY, Map.of(
                AUTH_SOURCE_CONFIGURATION_KEY, authSource,
                CHECKPOINT_INTERVAL_CONFIGURATION_KEY, checkpointInterval,
                DATABASE_CONFIGURATION_KEY, database,
                PASSWORD_CONFIGURATION_KEY, password,
                USERNAME_CONFIGURATION_KEY, username,
                SCHEMA_ENFORCED_CONFIGURATION_KEY, isSchemaEnforced)));
    final MongoDbSourceConfig sourceConfig = new MongoDbSourceConfig(rawConfig);
    assertNotNull(sourceConfig);
    assertEquals(authSource, sourceConfig.getAuthSource());
    assertEquals(checkpointInterval, sourceConfig.getCheckpointInterval());
    assertEquals(database, sourceConfig.getDatabaseName());
    assertEquals(password, sourceConfig.getPassword());
    assertEquals(OptionalInt.of(queueSize), sourceConfig.getQueueSize());
    assertEquals(rawConfig.get(DATABASE_CONFIG_CONFIGURATION_KEY), sourceConfig.getDatabaseConfig());
    assertEquals(sampleSize, sourceConfig.getSampleSize());
    assertEquals(username, sourceConfig.getUsername());
    assertEquals(isSchemaEnforced, sourceConfig.getEnforceSchema());
  }

  @Test
  void testCreatingInvalidMongoDbSourceConfig() {
    assertThrows(IllegalArgumentException.class, () -> new MongoDbSourceConfig(Jsons.jsonNode(Map.of())));
  }

  @Test
  void testDefaultValues() {
    final JsonNode rawConfig = Jsons.jsonNode(Map.of(DATABASE_CONFIG_CONFIGURATION_KEY, Map.of()));
    final MongoDbSourceConfig sourceConfig = new MongoDbSourceConfig(rawConfig);
    assertNotNull(sourceConfig);
    assertEquals(DEFAULT_AUTH_SOURCE, sourceConfig.getAuthSource());
    assertEquals(CHECKPOINT_INTERVAL, sourceConfig.getCheckpointInterval());
    assertEquals(null, sourceConfig.getDatabaseName());
    assertEquals(null, sourceConfig.getPassword());
    assertEquals(OptionalInt.empty(), sourceConfig.getQueueSize());
    assertEquals(rawConfig.get(DATABASE_CONFIG_CONFIGURATION_KEY), sourceConfig.getDatabaseConfig());
    assertEquals(DEFAULT_DISCOVER_SAMPLE_SIZE, sourceConfig.getSampleSize());
    assertEquals(null, sourceConfig.getUsername());
  }

}
