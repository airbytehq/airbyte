/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.util.function.Function;
import org.junit.jupiter.api.Test;

class DataAdapterTest {

  private final JsonNode testData = Jsons.deserialize("{\"attr1\" : \"CCC\", \"obj1\" : [{\"sub1\" : \"BBB\"}, {\"sub1\" : \"CCC\"}]}");
  private final Function<JsonNode, JsonNode> replaceCCCFunction = jsonNode -> {
    if (jsonNode.isTextual()) {
      String textValue = jsonNode.textValue().replaceAll("CCC", "FFF");
      return Jsons.jsonNode(textValue);
    } else
      return jsonNode;
  };

  @Test
  public void checkSkipAll() {
    final JsonNode data = testData.deepCopy();
    final DataAdapter adapter = new DataAdapter(jsonNode -> false, replaceCCCFunction);
    adapter.adapt(data);

    assertEquals(testData, data);
  }

  @Test
  public void checkSkip() {
    final JsonNode data = testData.deepCopy();
    final DataAdapter adapter = new DataAdapter(jsonNode -> jsonNode.isTextual() && jsonNode.textValue().contains("BBB"), replaceCCCFunction);
    adapter.adapt(data);

    assertEquals(testData, data);
  }

  @Test
  public void checkAdapt() {
    final JsonNode data = testData.deepCopy();
    final DataAdapter adapter = new DataAdapter(jsonNode -> jsonNode.isTextual() && jsonNode.textValue().contains("CCC"), replaceCCCFunction);
    adapter.adapt(data);
    System.out.println(data);

    assertNotEquals(testData, data);
    assert (data.findValues("sub1").stream().anyMatch(jsonNode -> jsonNode.isTextual() && jsonNode.textValue().equals("FFF")));
    assert (data.findValues("attr1").stream().anyMatch(jsonNode -> jsonNode.isTextual() && jsonNode.textValue().equals("FFF")));
  }

}
