/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import static io.airbyte.protocol.models.JsonSchemaType.DATE_TIME;
import static io.airbyte.protocol.models.JsonSchemaType.TIMESTAMP_WITH_TIMEZONE;
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
    JsonSchemaType build = new JsonSchemaType.Builder()
        .withType(JsonSchemaPrimitive.STRING)
        .withFormat(DATE_TIME)
        .build();
    JsonSchemaType build1 = new JsonSchemaType.Builder()
        .withType(JsonSchemaPrimitive.STRING)
        .withFormat(DATE_TIME)
        .build();
    JsonSchemaType build2 = new JsonSchemaType.Builder()
        .withType(JsonSchemaPrimitive.STRING)
        .withFormat(TIMESTAMP_WITH_TIMEZONE)
        .build();
    JsonSchemaType build3 = JsonSchemaType.STRING;
    JsonSchemaType build4 = JsonSchemaType.STRING;;
    for (final AirbyteProtocolSchema value : AirbyteProtocolSchema.values()) {
      assertTrue(Files.exists(value.getFile().toPath()));
    }
  }

}
