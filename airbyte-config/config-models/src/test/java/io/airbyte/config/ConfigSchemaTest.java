/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import org.junit.jupiter.api.Test;

class ConfigSchemaTest {

  @Test
  void testFile() throws IOException {
    final String schema = Files.readString(ConfigSchema.STATE.getConfigSchemaFile().toPath(), StandardCharsets.UTF_8);
    assertTrue(schema.contains("title"));
  }

  @Test
  void testPrepareKnownSchemas() {
    for (final ConfigSchema value : ConfigSchema.values()) {
      assertTrue(Files.exists(value.getConfigSchemaFile().toPath()), value.getConfigSchemaFile().toPath().toString() + " does not exist");
    }
  }

}
