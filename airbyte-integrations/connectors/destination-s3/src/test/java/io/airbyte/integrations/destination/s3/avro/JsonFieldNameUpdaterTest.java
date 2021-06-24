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

package io.airbyte.integrations.destination.s3.avro;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import java.io.IOException;
import java.util.Map.Entry;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

class JsonFieldNameUpdaterTest {

  @Test
  public void testFieldNameUpdate() throws IOException {
    JsonNode testCases = Jsons.deserialize(MoreResources.readResource("parquet/json_field_name_updater/test_case.json"));
    for (JsonNode testCase : testCases) {
      JsonNode nameMap = testCase.get("nameMap");
      JsonFieldNameUpdater nameUpdater = new JsonFieldNameUpdater(
          MoreIterators.toList(nameMap.fields()).stream()
              .collect(Collectors.toMap(Entry::getKey, e -> e.getValue().asText())));

      JsonNode original = testCase.get("original");
      JsonNode updated = testCase.get("updated");

      assertEquals(updated, nameUpdater.getJsonWithStandardizedFieldNames(original));
      assertEquals(original, nameUpdater.getJsonWithOriginalFieldNames(updated));
    }
  }

}
