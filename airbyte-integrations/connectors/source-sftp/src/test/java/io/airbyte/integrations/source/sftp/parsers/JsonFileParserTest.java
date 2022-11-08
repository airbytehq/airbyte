/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp.parsers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JsonFileParserTest {

  public static final String LOG_FILE_JSON = "log-test.json";
  private final JsonFileParser jsonFileParser = new JsonFileParser();
  private ArrayNode expectedNode;

  @BeforeEach
  void setUp() {
    JsonNode row1 = Jsons.jsonNode(ImmutableMap.builder()
        .put("id", 1)
        .put("log", "text1")
        .put("created_at", "04192022")
        .build());
    JsonNode row2 = Jsons.jsonNode(ImmutableMap.builder()
        .put("id", 2)
        .put("log", "text2")
        .put("created_at", "04202022")
        .build());
    expectedNode = Jsons.arrayNode()
        .add(row1)
        .add(row2);
  }

  @Test
  void parseFileTest() throws Exception {
    InputStream stream = Thread.currentThread().getContextClassLoader()
        .getResourceAsStream(LOG_FILE_JSON);

    List<JsonNode> jsonNodes = jsonFileParser.parseFile(new ByteArrayInputStream(stream.readAllBytes()));
    assertNotNull(jsonNodes);
    assertEquals(1, jsonNodes.size());
    assertEquals(expectedNode, jsonNodes.get(0));
  }

  @Test
  void parseFileFirstLineTest() throws Exception {
    InputStream stream = Thread.currentThread().getContextClassLoader()
        .getResourceAsStream(LOG_FILE_JSON);

    JsonNode jsonNode = jsonFileParser.parseFileFirstEntity(new ByteArrayInputStream(stream.readAllBytes()));
    assertNotNull(jsonNode);
    assertEquals(expectedNode, jsonNode);
  }

}
