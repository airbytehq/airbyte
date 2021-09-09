/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
    JsonNode data = testData.deepCopy();
    DataAdapter adapter = new DataAdapter(jsonNode -> false, replaceCCCFunction);
    adapter.adapt(data);

    assertEquals(testData, data);
  }

  @Test
  public void checkSkip() {
    JsonNode data = testData.deepCopy();
    DataAdapter adapter = new DataAdapter(jsonNode -> jsonNode.isTextual() && jsonNode.textValue().contains("BBB"), replaceCCCFunction);
    adapter.adapt(data);

    assertEquals(testData, data);
  }

  @Test
  public void checkAdapt() {
    JsonNode data = testData.deepCopy();
    DataAdapter adapter = new DataAdapter(jsonNode -> jsonNode.isTextual() && jsonNode.textValue().contains("CCC"), replaceCCCFunction);
    adapter.adapt(data);
    System.out.println(data);

    assertNotEquals(testData, data);
    assert (data.findValues("sub1").stream().anyMatch(jsonNode -> jsonNode.isTextual() && jsonNode.textValue().equals("FFF")));
    assert (data.findValues("attr1").stream().anyMatch(jsonNode -> jsonNode.isTextual() && jsonNode.textValue().equals("FFF")));
  }

}
