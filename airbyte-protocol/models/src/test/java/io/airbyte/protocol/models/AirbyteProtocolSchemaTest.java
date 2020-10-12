package io.airbyte.protocol.models;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

class AirbyteProtocolSchemaTest {

  @Test
  void testFile() throws IOException {
    final String schema = Files.readString(AirbyteProtocolSchema.MESSAGE.getFile().toPath(), StandardCharsets.UTF_8);
    assertTrue(schema.contains("title"));
  }

  @Test
  void testPrepareKnownSchemas() {
    for (AirbyteProtocolSchema value : AirbyteProtocolSchema.values()) {
      assertTrue(Files.exists(value.getFile().toPath()));
    }
  }

}
