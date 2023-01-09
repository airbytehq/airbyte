/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteMessage.Type;
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

  @Test
  void testVersionedObjectsAccessibility() {
    final var message = new io.airbyte.protocol.models.AirbyteMessage()
        .withType(Type.SPEC);
    final var messageV0 = new io.airbyte.protocol.models.v0.AirbyteMessage()
        .withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.SPEC);

    // This only works as long as the default version and v0 are equal
    final var deserializedMessage = Jsons.deserialize(Jsons.serialize(message), io.airbyte.protocol.models.v0.AirbyteMessage.class);
    assertEquals(messageV0, deserializedMessage);
  }

}
