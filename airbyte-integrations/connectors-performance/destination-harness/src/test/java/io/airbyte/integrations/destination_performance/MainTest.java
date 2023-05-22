/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_performance;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

class MainTest {

  @Test
  void testDuplicateStreams() throws JsonProcessingException {
    final String simpleCatalog = """
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
    final ObjectMapper objectMapper = new ObjectMapper();
    final JsonNode root = objectMapper.readTree(simpleCatalog);
    final int duplicateFactor = 10;
    Main.duplicateStreams(root, duplicateFactor);
    assertEquals(duplicateFactor, root.get("streams").size());
    assertEquals("users9", root.path("streams").get(9).path("stream").path("name").asText());
  }

}
