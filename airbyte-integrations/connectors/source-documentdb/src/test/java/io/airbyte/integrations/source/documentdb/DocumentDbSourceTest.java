/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.documentdb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.commons.json.Jsons;
import java.util.Map;
import org.junit.jupiter.api.Test;

class DocumentDbSourceTest {

  @Test
  void buildsDocumentDbSafeConnectionString() {
    final var config = Jsons.jsonNode(Map.of("host", "localhost", "port", 10260, "databases", java.util.List.of("db")));
    assertEquals("mongodb://localhost:10260/?retryWrites=false&tls=true&directConnection=true&readPreference=primaryPreferred&authSource=admin",
        DocumentDbSource.buildConnectionString(config));
  }

  @Test
  void preservesCredentialsFromConnectionString() {
    final var config = Jsons
        .jsonNode(Map.of("connection_string", "mongodb://reader:secret@localhost:10260/?retryWrites=true", "databases", java.util.List.of("db")));
    assertEquals(
        "mongodb://reader:secret@localhost:10260/?retryWrites=false&tls=true&directConnection=true&readPreference=primaryPreferred&authSource=admin",
        DocumentDbSource.buildConnectionString(config));
  }

  @Test
  void rejectsSrvConnectionStrings() {
    final var config = Jsons.jsonNode(Map.of("connection_string", "mongodb+srv://example.test/", "databases", java.util.List.of("db")));
    assertThrows(IllegalArgumentException.class, () -> DocumentDbSource.buildConnectionString(config));
  }

}
