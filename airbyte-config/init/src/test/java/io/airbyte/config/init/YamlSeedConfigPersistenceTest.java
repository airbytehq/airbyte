/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.init;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import java.io.IOException;
import java.net.URI;
import java.util.Collections;
import java.util.Map;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

class YamlSeedConfigPersistenceTest {

  private static YamlSeedConfigPersistence persistence;

  @BeforeAll
  static void setup() throws IOException {
    persistence = new YamlSeedConfigPersistence(YamlSeedConfigPersistence.DEFAULT_SEED_DEFINITION_RESOURCE_CLASS);
  }

  @Test
  void testGetConfig() throws Exception {
    // source
    final String mySqlSourceId = "435bb9a5-7887-4809-aa58-28c27df0d7ad";
    final StandardSourceDefinition mysqlSource = persistence
        .getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, mySqlSourceId, StandardSourceDefinition.class);
    assertEquals(mySqlSourceId, mysqlSource.getSourceDefinitionId().toString());
    assertEquals("MySQL", mysqlSource.getName());
    assertEquals("airbyte/source-mysql", mysqlSource.getDockerRepository());
    assertEquals("https://docs.airbyte.io/integrations/sources/mysql", mysqlSource.getDocumentationUrl());
    assertEquals("mysql.svg", mysqlSource.getIcon());
    assertEquals(URI.create("https://docs.airbyte.io/integrations/sources/mysql"), mysqlSource.getSpec().getDocumentationUrl());
    assertEquals(true, mysqlSource.getPublic());
    assertEquals(false, mysqlSource.getCustom());

    // destination
    final String s3DestinationId = "4816b78f-1489-44c1-9060-4b19d5fa9362";
    final StandardDestinationDefinition s3Destination = persistence
        .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, s3DestinationId, StandardDestinationDefinition.class);
    assertEquals(s3DestinationId, s3Destination.getDestinationDefinitionId().toString());
    assertEquals("S3", s3Destination.getName());
    assertEquals("airbyte/destination-s3", s3Destination.getDockerRepository());
    assertEquals("https://docs.airbyte.io/integrations/destinations/s3", s3Destination.getDocumentationUrl());
    assertEquals(URI.create("https://docs.airbyte.io/integrations/destinations/s3"), s3Destination.getSpec().getDocumentationUrl());
    assertEquals(true, s3Destination.getPublic());
    assertEquals(false, s3Destination.getCustom());
  }

  @Test
  void testGetInvalidConfig() {
    assertThrows(
        UnsupportedOperationException.class,
        () -> persistence.getConfig(ConfigSchema.STANDARD_SYNC, "invalid_id", StandardSync.class));
    assertThrows(
        ConfigNotFoundException.class,
        () -> persistence.getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, "invalid_id", StandardWorkspace.class));
  }

  @Test
  void testDumpConfigs() {
    final Map<String, Stream<JsonNode>> allSeedConfigs = persistence.dumpConfigs();
    assertEquals(2, allSeedConfigs.size());
    assertTrue(allSeedConfigs.get(ConfigSchema.STANDARD_SOURCE_DEFINITION.name()).findAny().isPresent());
    assertTrue(allSeedConfigs.get(ConfigSchema.STANDARD_DESTINATION_DEFINITION.name()).findAny().isPresent());
  }

  @Test
  void testWriteMethods() {
    assertThrows(UnsupportedOperationException.class, () -> persistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, "id", new Object()));
    assertThrows(UnsupportedOperationException.class, () -> persistence.replaceAllConfigs(Collections.emptyMap(), false));
  }

}
