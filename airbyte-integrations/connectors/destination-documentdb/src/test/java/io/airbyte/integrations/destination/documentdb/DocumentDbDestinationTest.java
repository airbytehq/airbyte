/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.documentdb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.commons.json.Jsons;
import java.util.Map;
import org.junit.jupiter.api.Test;

class DocumentDbDestinationTest {
  @Test
  void buildsDocumentDbSafeConnectionString() {
    final var config = Jsons.jsonNode(Map.of("host", "localhost", "port", 10260, "database", "db"));
    assertEquals("mongodb://localhost:10260/db?retryWrites=false&tls=true&directConnection=true&readPreference=primaryPreferred&authSource=admin",
        DocumentDbDestination.buildConnectionString(config));
  }

  @Test
  void preservesCredentialsFromConnectionString() {
    final var config = Jsons.jsonNode(Map.of("connection_string", "mongodb://writer:secret@localhost:10260/?retryWrites=true", "database", "db"));
    assertEquals("mongodb://writer:secret@localhost:10260/db?retryWrites=false&tls=true&directConnection=true&readPreference=primaryPreferred&authSource=admin",
        DocumentDbDestination.buildConnectionString(config));
  }

  @Test
  void rejectsSrvConnectionStrings() {
    final var config = Jsons.jsonNode(Map.of("connection_string", "mongodb+srv://example.test/", "database", "db"));
    assertThrows(IllegalArgumentException.class, () -> DocumentDbDestination.buildConnectionString(config));
  }
}