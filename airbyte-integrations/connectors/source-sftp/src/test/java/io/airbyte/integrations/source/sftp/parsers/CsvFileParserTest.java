/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp.parsers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class CsvFileParserTest {

  public static final String LOG_FILE_CSV = "log-test.csv";
  private final CsvFileParser csvFileParser = new CsvFileParser();
  private JsonNode expectedFirstNode;
  private JsonNode expectedSecondNode;

  @BeforeEach
  void setUp() {
    expectedFirstNode = Jsons.jsonNode(ImmutableMap.builder()
        .put("id", "1")
        .put("log", "text1")
        .put("created_at", "04192022")
        .build());
    expectedSecondNode = Jsons.jsonNode(ImmutableMap.builder()
        .put("id", "2")
        .put("log", "text2")
        .put("created_at", "04202022")
        .build());
  }

  @Test
  void parseFileTest() throws Exception {
    InputStream stream = Thread.currentThread().getContextClassLoader()
        .getResourceAsStream(LOG_FILE_CSV);

    List<JsonNode> jsonNodes = csvFileParser.parseFile(new ByteArrayInputStream(stream.readAllBytes()));
    assertNotNull(jsonNodes);
    assertEquals(2, jsonNodes.size());
    assertEquals(expectedFirstNode, jsonNodes.get(0));
    assertEquals(expectedSecondNode, jsonNodes.get(1));
  }

  @Test
  void parseFileFirstLineTest() throws Exception {
    InputStream stream = Thread.currentThread().getContextClassLoader()
        .getResourceAsStream(LOG_FILE_CSV);

    JsonNode jsonNode = csvFileParser.parseFileFirstEntity(new ByteArrayInputStream(stream.readAllBytes()));
    assertNotNull(jsonNode);
    assertEquals(expectedFirstNode, jsonNode);
  }

}
