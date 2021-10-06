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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Map;

/**
 * This helper class tracks whether a Json has special field name that needs to be replaced with a
 * standardized one, and can perform the replacement when necessary.
 */
public class JsonFieldNameUpdater {

  // A map from original name to standardized name.
  private final Map<String, String> standardizedNames;

  public JsonFieldNameUpdater(Map<String, String> standardizedNames) {
    this.standardizedNames = ImmutableMap.copyOf(standardizedNames);
  }

  public boolean hasNameUpdate() {
    return standardizedNames.size() > 0;
  }

  public JsonNode getJsonWithStandardizedFieldNames(JsonNode input) {
    if (!hasNameUpdate()) {
      return input;
    }
    String jsonString = Jsons.serialize(input);
    for (Map.Entry<String, String> entry : standardizedNames.entrySet()) {
      jsonString = jsonString.replaceAll(quote(entry.getKey()), quote(entry.getValue()));
    }
    return Jsons.deserialize(jsonString);
  }

  public JsonNode getJsonWithOriginalFieldNames(JsonNode input) {
    if (!hasNameUpdate()) {
      return input;
    }
    String jsonString = Jsons.serialize(input);
    for (Map.Entry<String, String> entry : standardizedNames.entrySet()) {
      jsonString = jsonString.replaceAll(quote(entry.getValue()), quote(entry.getKey()));
    }
    return Jsons.deserialize(jsonString);
  }

  @Override
  public String toString() {
    return standardizedNames.toString();
  }

  private static String quote(String input) {
    return "\"" + input + "\"";
  }

}
