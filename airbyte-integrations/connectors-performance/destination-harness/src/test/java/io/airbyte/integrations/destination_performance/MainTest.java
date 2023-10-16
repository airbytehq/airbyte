/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_performance;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.SyncMode;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

class MainTest {

  private static String simpleCatalog;

  @BeforeAll
  public static void setup() {
    simpleCatalog = """
                      {
                        "streams": [
                          {
                            "stream": {
                              "name": "users",
                              "namespace": "PERF_TEST_HARNESS",
                              "json_schema": {
                                "type": "object",
                                "properties": {
                                  "id": {
                                    "type": "number",
                                    "airbyte_type": "integer"
                                  },
                                  "academic_degree": {
                                    "type": "string"
                                  }
                                }
                              },
                              "default_cursor_field": [],
                              "supported_sync_modes": ["full_refresh", "incremental"],
                              "source_defined_primary_key": [["id"]]
                            },
                            "sync_mode": "full_refresh",
                            "primary_key": [["id"]],
                            "cursor_field": ["updated_at"],
                            "destination_sync_mode": "overwrite"
                          }
                        ]
                      }
                    """;
  }

  @Test
  void testDuplicateStreams() throws JsonProcessingException {
    final ObjectMapper objectMapper = new ObjectMapper();
    final JsonNode root = objectMapper.readTree(simpleCatalog);
    final JsonNode duplicateRoot = root.deepCopy();
    final int duplicateFactor = 10;
    Main.duplicateStreams(duplicateRoot, duplicateFactor);
    assertEquals(duplicateFactor, duplicateRoot.get("streams").size());
    assertEquals("users9", duplicateRoot.path("streams").get(9).path("stream").path("name").asText());
  }

  @Test
  void testUpdateSyncModeIncrementalAppend() throws JsonProcessingException {
    final ObjectMapper objectMapper = new ObjectMapper();
    final JsonNode root = objectMapper.readTree(simpleCatalog);
    final JsonNode duplicateRoot = root.deepCopy();
    Main.updateSyncMode(duplicateRoot, "incremental");
    assertEquals(SyncMode.INCREMENTAL.toString(), duplicateRoot.path("streams").get(0).path("sync_mode").asText());
    assertEquals(DestinationSyncMode.APPEND.toString(), duplicateRoot.path("streams").get(0).path("destination_sync_mode").asText());
  }

  @Test
  void testUpdateSyncModeFullRefreshNoop() throws JsonProcessingException {
    // expects a no-op when updating sync mode to full_refresh
    final ObjectMapper objectMapper = new ObjectMapper();
    final JsonNode root = objectMapper.readTree(simpleCatalog);
    final JsonNode duplicateRoot = root.deepCopy();
    Main.updateSyncMode(duplicateRoot, "full_refresh");
    assertEquals(SyncMode.FULL_REFRESH.toString(), duplicateRoot.path("streams").get(0).path("sync_mode").asText());
    assertEquals(DestinationSyncMode.OVERWRITE.toString(), duplicateRoot.path("streams").get(0).path("destination_sync_mode").asText());
  }

}
