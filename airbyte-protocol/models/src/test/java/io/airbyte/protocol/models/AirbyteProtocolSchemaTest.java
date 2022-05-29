/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import org.junit.jupiter.api.Test;

class AirbyteProtocolSchemaTest {

  @Test
  void testFile() throws IOException {
    final String schema = Files.readString(AirbyteProtocolSchema.PROTOCOL.getFile().toPath(), StandardCharsets.UTF_8);
    assertTrue(schema.contains("title"));
  }

  @Test
  void testPrepareKnownSchemas() {
    for (final AirbyteProtocolSchema value : AirbyteProtocolSchema.values()) {
      assertTrue(Files.exists(value.getFile().toPath()));
    }
  }

  @Test
  void testJsonSchemaType() {
    for (final AirbyteProtocolSchema value : AirbyteProtocolSchema.values()) {
      assertTrue(Files.exists(value.getFile().toPath()));
    }
  }

}
