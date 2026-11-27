/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.clickhouse;

import static org.junit.jupiter.api.Assertions.assertFalse;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.yaml.Yamls;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class ClickHouseReleaseMetadataTest {

  @Test
  void preservesTemporalTypeBreakingChangeDeclaration() throws IOException {
    final JsonNode metadata = Yamls.deserialize(Files.readString(Path.of("metadata.yaml")));
    final JsonNode data = metadata.path("data");
    final JsonNode breakingChange = data.path("releases").path("breakingChanges").path("0.4.0");

    assertFalse(breakingChange.isMissingNode());
    assertFalse(breakingChange.path("message").asText().isBlank());
    assertFalse(breakingChange.path("upgradeDeadline").asText().isBlank());
  }

}
